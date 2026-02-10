# :keyboard: CLI Usage

Talk2Scene uses Hydra for configuration. All config values can be overridden via CLI.

## :play_or_pause_button: Modes

### :repeat: Batch Mode
Process an audio file end-to-end:
```bash
uv run talk2scene mode=batch
```

### :memo: Text Mode
Process a transcript JSONL directly into scene events (skip audio/transcription):
```bash
uv run talk2scene mode=text io.input.text_file=input/sample_transcript.jsonl
```

Input format — one JSON object per line:
```json
{"type": "transcript", "start": 0.0, "end": 3.0, "text": "Hello everyone.", "speaker_id": "researcher"}
```

### :satellite: Streaming Mode
Consume from Redis streams in realtime. Supports two input streams simultaneously:

- :speech_balloon: **stream:stt** — pre-transcribed text (higher priority, skips Whisper)
- :studio_microphone: **stream:mic** — raw PCM audio (processed through rolling window + Whisper)

```bash
uv run talk2scene mode=stream
```

When both streams have messages, STT messages are processed first. See [Redis Audio Streaming](redis-streaming.md) for stream formats and publishing examples.

### :clapper: Video Mode
Render session events into a video with subtitles. Scenes are rendered in parallel using multiprocessing, then assembled via ffmpeg concat demuxer:
```bash
uv run talk2scene mode=video session_id=my_session
```

Supported formats: `webm` (default), `mp4`, `avi`.

```bash
# MP4 output, no preview
uv run talk2scene mode=video session_id=my_session render.video.format=mp4 render.video.preview=false
```

### :framed_picture: Render Mode
Render a scene to PNG:
```bash
uv run talk2scene render.scene=true render.scene_file=scene.json
```

### :bar_chart: Evaluation Mode
Run scene evaluation:
```bash
uv run talk2scene eval.run=true
```

### :art: Generate Assets
Create placeholder assets:
```bash
uv run talk2scene mode=generate-assets
```

## :level_slider: Common Overrides

```bash
# Custom session ID
uv run talk2scene mode=batch session_id=my_session

# Change Whisper model
uv run talk2scene mode=batch model.whisper.model_size=medium

# Change canvas size
uv run talk2scene render.scene=true render.canvas.width=512 render.canvas.height=512

# Change log level
uv run talk2scene mode=batch log_level=DEBUG

# Enable live scene rendering in stream mode
uv run talk2scene mode=stream render.scene_on_event=true
```
