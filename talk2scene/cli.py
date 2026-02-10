"""Talk2Scene CLI entry point with Hydra configuration."""

import json
import logging
import signal
import sys
from pathlib import Path

import hydra
from omegaconf import DictConfig, OmegaConf

from talk2scene.session import SessionManager
from talk2scene.whitelist import load_whitelist
from talk2scene.outputs import OutputWriter
from talk2scene.performance import PerformanceMonitor

logger = logging.getLogger(__name__)

_shutdown_requested = False


def _signal_handler(signum, frame):
    global _shutdown_requested
    logger.info(f"Received signal {signum}, initiating graceful shutdown...")
    _shutdown_requested = True


def _validate_config(cfg: DictConfig):
    load_whitelist(cfg.assets.whitelist_path)
    logger.info("Configuration validated successfully")


def run_batch(cfg: DictConfig, session: SessionManager, monitor: PerformanceMonitor):
    from talk2scene.audio import load_batch_audio
    from talk2scene.transcription import Transcriber, append_transcript_events, build_transcript_snapshot
    from talk2scene.scene_gen import SceneGenerator
    from talk2scene.state_machine import StateManager

    writer = OutputWriter(session.session_dir)
    state_mgr = StateManager(
        cooldown_ms=cfg.character.characters.default.transition.cooldown_ms,
        hold_frames=cfg.character.characters.default.transition.hold_frames,
        fade_ms=cfg.character.characters.default.transition.fade_ms,
    )

    # Find audio file
    audio_dir = Path(cfg.io.input.audio_dir)
    audio_files = []
    for fmt in cfg.io.input.supported_formats:
        audio_files.extend(audio_dir.glob(f"*.{fmt}"))

    if not audio_files:
        logger.error(f"No audio files found in {audio_dir}")
        return

    audio_path = str(audio_files[0])
    logger.info(f"Processing audio: {audio_path}")

    # Normalize audio
    monitor.start("audio_normalize")
    wav_path = load_batch_audio(audio_path, str(session.session_dir))
    monitor.stop("audio_normalize")

    # Transcribe
    monitor.start("transcription")
    transcriber = Transcriber(
        model_size=cfg.model.whisper.model_size,
        language=cfg.model.whisper.language,
        device=cfg.model.whisper.device,
    )
    transcript_events = transcriber.transcribe_file(wav_path)
    monitor.stop("transcription")

    # Write transcript
    transcript_jsonl = session.get_path("transcript.jsonl")
    append_transcript_events(transcript_events, transcript_jsonl)
    build_transcript_snapshot(transcript_jsonl, session.get_path("transcript.json"))

    # Generate scenes
    monitor.start("scene_generation")
    scene_gen = SceneGenerator(
        model=cfg.model.llm.model,
        temperature=cfg.model.llm.temperature,
        max_tokens=cfg.model.llm.max_tokens,
    )
    scene_events = scene_gen.generate(transcript_events)
    monitor.stop("scene_generation")

    # Apply state machine and write events
    for event in scene_events:
        if _shutdown_requested:
            break
        transition = state_mgr.apply_event(event)
        writer.append_event(event)
        if transition.get("changes"):
            writer.append_event(transition)

    writer.finalize()
    logger.info(f"Batch processing complete: {writer.event_count} events written")


def run_text(cfg: DictConfig, session: SessionManager, monitor: PerformanceMonitor):
    """Process a transcript JSONL file directly into scene events (skip audio/transcription)."""
    from talk2scene.transcription import append_transcript_events, build_transcript_snapshot
    from talk2scene.scene_gen import SceneGenerator
    from talk2scene.state_machine import StateManager

    text_file = cfg.io.input.text_file
    if not text_file:
        logger.error("No text file specified. Use: io.input.text_file=path/to/transcript.jsonl")
        return

    text_path = Path(text_file)
    if not text_path.exists():
        logger.error(f"Text file not found: {text_path}")
        return

    writer = OutputWriter(session.session_dir)
    state_mgr = StateManager(
        cooldown_ms=cfg.character.characters.default.transition.cooldown_ms,
        hold_frames=cfg.character.characters.default.transition.hold_frames,
        fade_ms=cfg.character.characters.default.transition.fade_ms,
    )

    # Read transcript events from JSONL
    transcript_events = []
    with open(text_path) as f:
        for line in f:
            line = line.strip()
            if line:
                transcript_events.append(json.loads(line))

    logger.info(f"Loaded {len(transcript_events)} transcript events from {text_path}")

    # Save transcript copy into session
    transcript_jsonl = session.get_path("transcript.jsonl")
    append_transcript_events(transcript_events, transcript_jsonl)
    build_transcript_snapshot(transcript_jsonl, session.get_path("transcript.json"))

    # Generate scenes
    monitor.start("scene_generation")
    scene_gen = SceneGenerator(
        model=cfg.model.llm.model,
        temperature=cfg.model.llm.temperature,
        max_tokens=cfg.model.llm.max_tokens,
    )
    scene_events = scene_gen.generate(transcript_events)
    monitor.stop("scene_generation")

    # Apply state machine and write events
    for event in scene_events:
        if _shutdown_requested:
            break
        transition = state_mgr.apply_event(event)
        writer.append_event(event)
        if transition.get("changes"):
            writer.append_event(transition)

    writer.finalize()
    logger.info(f"Text processing complete: {writer.event_count} events written")


def run_stream(cfg: DictConfig, session: SessionManager, monitor: PerformanceMonitor):
    import tempfile

    from talk2scene.audio import RedisAudioConsumer, chunks_to_wav
    from talk2scene.transcription import Transcriber, append_transcript_events
    from talk2scene.scene_gen import SceneGenerator
    from talk2scene.state_machine import StateManager

    writer = OutputWriter(session.session_dir)
    state_mgr = StateManager(
        cooldown_ms=cfg.character.characters.default.transition.cooldown_ms,
        hold_frames=cfg.character.characters.default.transition.hold_frames,
        fade_ms=cfg.character.characters.default.transition.fade_ms,
    )

    consumer = RedisAudioConsumer(cfg.stream)
    transcriber = Transcriber(
        model_size=cfg.model.whisper.model_size,
        language=cfg.model.whisper.language,
        device=cfg.model.whisper.device,
    )
    scene_gen = SceneGenerator(
        model=cfg.model.llm.model,
        temperature=cfg.model.llm.temperature,
    )

    stt_stream_key = cfg.stream.redis.stt_stream_key
    rolling_chunks: list[bytes] = []
    rolling_window = cfg.stream.audio.rolling_window_s
    chunk_duration = cfg.stream.audio.chunk_duration_ms / 1000.0

    render_on_event = cfg.render.get("scene_on_event", False)
    asset_dirs = OmegaConf.to_container(cfg.assets.asset_dirs, resolve=True) if render_on_event else None
    canvas_size = (cfg.render.canvas.width, cfg.render.canvas.height) if render_on_event else None

    logger.info("Starting Redis dual-stream consumer (stt + mic)...")
    try:
        for msg_id, stream_name, data in consumer.consume():
            if _shutdown_requested:
                break

            if stream_name == stt_stream_key:
                # STT path: pre-transcribed text, skip Whisper
                msg_type = data.get(b"type", b"").decode()
                text = data.get(b"text", b"").decode()
                if msg_type != "final" or not text.strip():
                    continue
                transcript_events = [{
                    "type": "transcript",
                    "start": float(data.get(b"start_time", 0)),
                    "end": float(data.get(b"end_time", 0)),
                    "text": text,
                    "speaker_id": "unknown",
                }]
            else:
                # Mic path: rolling window + Whisper
                audio_bytes = data.get(b"audio", b"")
                rolling_chunks.append(audio_bytes)
                max_chunks = int(rolling_window / chunk_duration)
                if len(rolling_chunks) > max_chunks:
                    rolling_chunks = rolling_chunks[-max_chunks:]

                monitor.start("transcription")
                wav_data = chunks_to_wav(rolling_chunks, cfg.stream.audio.sample_rate)
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as tmp:
                    tmp.write(wav_data)
                    tmp.flush()
                    transcript_events = transcriber.transcribe_file(tmp.name)
                monitor.stop("transcription")

            if transcript_events:
                append_transcript_events(
                    transcript_events, session.get_path("transcript.jsonl")
                )

                monitor.start("scene_generation")
                scene_events = scene_gen.generate(transcript_events)
                monitor.stop("scene_generation")

                for event in scene_events:
                    transition = state_mgr.apply_event(event)
                    writer.append_event(event)
                    if transition.get("changes"):
                        writer.append_event(transition)

                # Optionally render front page on each scene event batch
                if render_on_event and scene_events:
                    from talk2scene.renderer import render_scene_to_file
                    last = scene_events[-1]
                    scene_state = {k: last[k] for k in ("sta", "exp", "act", "bg", "cg") if k in last}
                    render_scene_to_file(
                        scene_state,
                        str(session.session_dir / "front_page.png"),
                        asset_dirs,
                        canvas_size,
                    )

    except KeyboardInterrupt:
        logger.info("Stream interrupted by user")
    finally:
        consumer.close()
        writer.finalize()
        logger.info(f"Stream processing ended: {writer.event_count} events")


def run_render(cfg: DictConfig, session: SessionManager, monitor: PerformanceMonitor):
    from talk2scene.renderer import render_scene_to_file

    scene_file = cfg.render.scene_file
    if not scene_file:
        # Try to load from session events
        events_path = session.get_path("events.jsonl")
        if events_path.exists():
            with open(events_path) as f:
                lines = [l.strip() for l in f if l.strip()]
            if lines:
                last_event = json.loads(lines[-1])
                scene_state = {
                    "sta": last_event.get("sta", "STA_Stand_Front"),
                    "exp": last_event.get("exp", "EXP_Neutral"),
                    "act": last_event.get("act", "ACT_None"),
                    "bg": last_event.get("bg", "BG_Lab_Modern"),
                    "cg": last_event.get("cg", "CG_None"),
                }
            else:
                logger.error("No events found to render")
                return
        else:
            logger.error("No scene file specified and no events found")
            return
    else:
        with open(scene_file) as f:
            scene_state = json.load(f)

    asset_dirs = OmegaConf.to_container(cfg.assets.asset_dirs, resolve=True)
    canvas = (cfg.render.canvas.width, cfg.render.canvas.height)

    monitor.start("render")
    output_path = str(session.get_path("scene_render.png"))
    render_scene_to_file(scene_state, output_path, asset_dirs, canvas)
    monitor.stop("render")
    logger.info(f"Scene rendered to: {output_path}")


def run_eval(cfg: DictConfig, monitor: PerformanceMonitor):
    from talk2scene.evaluation import run_evaluation

    asset_dirs = OmegaConf.to_container(cfg.assets.asset_dirs, resolve=True)
    canvas = (cfg.render.canvas.width, cfg.render.canvas.height)

    monitor.start("evaluation")
    results = run_evaluation(
        cases_dir=cfg.eval.cases_dir,
        expected_dir=cfg.eval.expected_dir,
        output_dir=cfg.eval.output_dir,
        diffs_dir=cfg.eval.diffs_dir,
        asset_dirs=asset_dirs,
        canvas_size=canvas,
        tolerance=cfg.eval.tolerance,
    )
    monitor.stop("evaluation")

    total = results["summary"]["total"]
    passed = results["summary"]["passed"]
    failed = results["summary"]["failed"]
    print(f"\nEvaluation Results: {passed}/{total} passed, {failed} failed")
    for case in results["cases"]:
        status = "PASS" if case["passed"] else "FAIL"
        detail = ""
        if "pixel_diff_pct" in case:
            detail = f" (diff: {case['pixel_diff_pct']}%)"
        if "note" in case:
            detail = f" ({case['note']})"
        print(f"  [{status}] {case['name']}{detail}")


def _find_subtitle_font() -> str | None:
    """Return the path string of the first available subtitle font, or None."""
    for fp in [
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
        "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
        "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ]:
        if Path(fp).exists():
            return fp
    return None


def _render_scene_frame(args: tuple) -> tuple[int, str, float]:
    """Worker function for multiprocessing: render one scene to a PNG file.

    Args is a tuple of:
        (idx, event_dict, asset_dirs, canvas_size, burn_subs, font_path, font_size, output_path)

    Returns (idx, output_path, duration).
    """
    from PIL import Image, ImageDraw, ImageFont
    from talk2scene.renderer import render_scene

    idx, event, asset_dirs, canvas_size, burn_subs, font_path, font_size, output_path = args

    scene_state = {k: event[k] for k in ("sta", "exp", "act", "bg", "cg")}
    img = render_scene(scene_state, asset_dirs, canvas_size)

    # Flatten alpha onto white
    bg = Image.new("RGBA", canvas_size, (255, 255, 255, 255))
    final = Image.alpha_composite(bg, img).convert("RGB")

    # Burn subtitle
    if burn_subs and event.get("text"):
        if font_path:
            font = ImageFont.truetype(font_path, font_size)
        else:
            font = ImageFont.load_default()
        draw = ImageDraw.Draw(final)
        text = event["text"]
        bbox = draw.textbbox((0, 0), text, font=font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        sx = (canvas_size[0] - tw) // 2
        sy = canvas_size[1] - 80
        pad = 10
        draw.rectangle(
            [sx - pad, sy - pad, sx + tw + pad, sy + th + pad],
            fill=(0, 0, 0, 180),
        )
        draw.text((sx, sy), text, fill=(255, 255, 255), font=font)

    final.save(output_path)
    duration = event["end"] - event["start"]
    return idx, output_path, duration


def _build_ffmpeg_cmd(concat_path: str, fps: int, crf: int, fmt: str, output_path: str) -> list[str]:
    """Build ffmpeg command using concat demuxer for per-scene durations."""
    base = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_path, "-r", str(fps)]
    if fmt == "webm":
        return base + ["-c:v", "libvpx-vp9", "-crf", str(crf), "-b:v", "0", "-pix_fmt", "yuv420p", output_path]
    elif fmt == "avi":
        return base + ["-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", str(crf), output_path]
    else:  # mp4
        return base + ["-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", str(crf), "-preset", "fast", output_path]


def run_video(cfg: DictConfig, session: SessionManager, monitor: PerformanceMonitor):
    """Render events.jsonl into a video with subtitles using parallel rendering."""
    import multiprocessing
    import os
    import subprocess

    events_path = session.get_path("events.jsonl")
    if not events_path.exists():
        logger.error("No events.jsonl in session. Run text/batch mode first.")
        return

    asset_dirs = OmegaConf.to_container(cfg.assets.asset_dirs, resolve=True)
    canvas_size = (cfg.render.canvas.width, cfg.render.canvas.height)
    fps = cfg.render.video.fps
    crf = cfg.render.video.crf
    fmt = cfg.render.video.format
    burn_subs = cfg.render.video.subtitle
    font_size = cfg.render.video.subtitle_font_size
    preview = cfg.render.video.preview

    # Load scene events
    scene_events = []
    with open(events_path) as f:
        for line in f:
            ev = json.loads(line.strip())
            if ev.get("type") == "scene":
                scene_events.append(ev)

    if not scene_events:
        logger.error("No scene events found in events.jsonl")
        return

    total_duration = max(ev["end"] for ev in scene_events)
    logger.info(
        f"Rendering video: {len(scene_events)} scenes, {total_duration:.1f}s, format={fmt} (parallel)"
    )

    # Resolve font path (picklable string, not PIL object)
    font_path = _find_subtitle_font() if burn_subs else None

    # Prepare frames directory and task tuples
    frames_dir = session.session_dir / "frames"
    frames_dir.mkdir(exist_ok=True)

    tasks = []
    for idx, ev in enumerate(scene_events):
        out = str(frames_dir / f"scene_{idx:05d}.png")
        tasks.append((idx, ev, asset_dirs, canvas_size, burn_subs, font_path, font_size, out))

    # Render scenes in parallel
    monitor.start("video_render")
    workers = min(os.cpu_count() or 1, len(tasks))
    logger.info(f"Rendering {len(tasks)} scene images with {workers} workers...")
    with multiprocessing.Pool(workers) as pool:
        results = pool.map(_render_scene_frame, tasks)
    monitor.stop("video_render")

    # Sort results by index and build concat file
    results.sort(key=lambda r: r[0])
    concat_path = str(frames_dir / "concat.txt")
    with open(concat_path, "w") as cf:
        for idx, frame_path, duration in results:
            # Use basename only; ffmpeg resolves relative to concat.txt location
            cf.write(f"file '{Path(frame_path).name}'\n")
            cf.write(f"duration {duration:.6f}\n")
        # ffmpeg concat needs last file repeated without duration
        if results:
            cf.write(f"file '{Path(results[-1][1]).name}'\n")

    # Encode with ffmpeg
    output_path = str(session.session_dir / f"scene_video.{fmt}")
    monitor.start("video_encode")
    cmd = _build_ffmpeg_cmd(concat_path, fps, crf, fmt, output_path)
    logger.info(f"Encoding video: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    monitor.stop("video_encode")

    if result.returncode != 0:
        logger.error(f"ffmpeg failed:\n{result.stderr}")
        return

    logger.info(f"Video saved to: {output_path}")
    print(f"Video: {output_path}")

    if preview:
        logger.info("Opening video preview...")
        subprocess.Popen(["xdg-open", output_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def run_generate_assets(cfg: DictConfig):
    from talk2scene.asset_gen import generate_all_placeholders

    canvas = (cfg.render.canvas.width, cfg.render.canvas.height)
    generate_all_placeholders(
        whitelist_path=cfg.assets.whitelist_path,
        asset_base="assets",
        canvas_size=canvas,
        force="--force" in sys.argv,
    )
    print("Placeholder assets generated successfully")


def _find_config_dir() -> str:
    """Find the conf directory relative to the project root."""
    # Check relative to CWD first
    cwd_conf = Path.cwd() / "conf"
    if cwd_conf.exists():
        return str(cwd_conf)
    # Check relative to this file (development layout)
    pkg_conf = Path(__file__).parent.parent / "conf"
    if pkg_conf.exists():
        return str(pkg_conf)
    raise FileNotFoundError("Cannot find conf/ directory")


def _print_help():
    print("""Talk2Scene - Convert audio dialogue into animated scene events

Usage: uv run talk2scene [OVERRIDES...]

Modes:
  mode=batch              Process audio file end-to-end
  mode=text               Process transcript JSONL into scene events
  mode=stream             Consume audio from Redis stream
  mode=video              Render session events into video (webm/mp4/avi)
  mode=generate-assets    Generate placeholder assets
  render.scene=true       Render a scene to PNG
  eval.run=true           Run scene evaluation

Common overrides:
  session_id=ID                     Set session ID
  io.input.text_file=path.jsonl     Transcript JSONL for text mode
  model.whisper.model_size=medium   Change Whisper model
  render.canvas.width=512           Change canvas width
  log_level=DEBUG                   Change log level

Config files: conf/config.yaml (see conf/ for all groups)
""")


def main():
    # Handle --help before Hydra
    if "--help" in sys.argv or "-h" in sys.argv:
        _print_help()
        return

    from hydra import compose, initialize_config_dir
    from hydra.core.global_hydra import GlobalHydra

    GlobalHydra.instance().clear()
    config_dir = _find_config_dir()

    # Filter out non-Hydra args
    overrides = [a for a in sys.argv[1:] if not a.startswith("-")]

    with initialize_config_dir(version_base=None, config_dir=config_dir):
        cfg = compose(config_name="config", overrides=overrides)
        _app_main(cfg)


def _app_main(cfg: DictConfig):
    # Setup logging
    logging.basicConfig(
        level=getattr(logging, cfg.log_level),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    # Register signal handlers
    signal.signal(signal.SIGINT, _signal_handler)
    signal.signal(signal.SIGTERM, _signal_handler)

    logger.info(f"Talk2Scene starting in {cfg.mode} mode")
    _validate_config(cfg)

    monitor = PerformanceMonitor()

    # Handle special modes
    if cfg.eval.run:
        run_eval(cfg, monitor)
        return

    if cfg.render.scene:
        session = SessionManager(
            base_dir=cfg.io.output.base_dir,
            session_id=cfg.session_id,
        )
        run_render(cfg, session, monitor)
        monitor.save(session.get_path("performance.json"))
        return

    if cfg.mode == "generate-assets":
        run_generate_assets(cfg)
        return

    # Main pipeline modes
    session = SessionManager(
        base_dir=cfg.io.output.base_dir,
        session_id=cfg.session_id,
    )
    logger.info(f"Session: {session.session_id}")

    try:
        if cfg.mode == "batch":
            run_batch(cfg, session, monitor)
        elif cfg.mode == "text":
            run_text(cfg, session, monitor)
        elif cfg.mode == "video":
            run_video(cfg, session, monitor)
        elif cfg.mode == "stream":
            run_stream(cfg, session, monitor)
        else:
            logger.error(f"Unknown mode: {cfg.mode}")
            sys.exit(1)
    finally:
        if _shutdown_requested:
            logger.info("Graceful shutdown: finalizing outputs...")
        session.finalize()
        monitor.save(session.get_path("performance.json"))
        logger.info(f"Session {session.session_id} finalized")


if __name__ == "__main__":
    main()
