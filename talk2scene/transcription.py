"""Whisper-based transcription with streaming support."""

import json
import logging
import tempfile
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class Transcriber:
    def __init__(self, model_size: str = "base", language: Optional[str] = None, device: str = "cpu"):
        self.language = language
        self.model = None
        self._use_api = False

        try:
            import whisper
            self.model = whisper.load_model(model_size, device=device)
            logger.info(f"Loaded local Whisper model: {model_size}")
        except ImportError:
            logger.info("Local whisper not installed, using OpenAI API for transcription")
            self._use_api = True

    def transcribe_file(self, audio_path: str) -> list[dict]:
        if self._use_api:
            return self._transcribe_api(audio_path)
        return self._transcribe_local(audio_path)

    def _transcribe_local(self, audio_path: str) -> list[dict]:
        opts = {"word_timestamps": True}
        if self.language:
            opts["language"] = self.language

        result = self.model.transcribe(audio_path, **opts)
        events = []
        for seg in result.get("segments", []):
            events.append({
                "type": "transcript",
                "start": seg["start"],
                "end": seg["end"],
                "text": seg["text"].strip(),
                "speaker_id": "unknown",
            })
        return events

    def _transcribe_api(self, audio_path: str) -> list[dict]:
        import openai

        client = openai.OpenAI()
        with open(audio_path, "rb") as f:
            result = client.audio.transcriptions.create(
                model="whisper-1",
                file=f,
                response_format="verbose_json",
                timestamp_granularities=["segment"],
            )

        events = []
        for seg in getattr(result, "segments", []):
            events.append({
                "type": "transcript",
                "start": seg.get("start", 0),
                "end": seg.get("end", 0),
                "text": seg.get("text", "").strip(),
                "speaker_id": "unknown",
            })

        # Fallback if no segments
        if not events and hasattr(result, "text") and result.text:
            events.append({
                "type": "transcript",
                "start": 0.0,
                "end": 0.0,
                "text": result.text.strip(),
                "speaker_id": "unknown",
            })

        return events

    def transcribe_chunk(self, audio_bytes: bytes, sample_rate: int = 16000) -> list[dict]:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as tmp:
            import wave
            with wave.open(tmp.name, "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(sample_rate)
                wf.writeframes(audio_bytes)
            return self.transcribe_file(tmp.name)


def append_transcript_events(events: list[dict], output_path: Path):
    with open(output_path, "a") as f:
        for ev in events:
            f.write(json.dumps(ev, ensure_ascii=False) + "\n")


def build_transcript_snapshot(jsonl_path: Path, json_path: Path):
    events = []
    if jsonl_path.exists():
        with open(jsonl_path) as f:
            for line in f:
                line = line.strip()
                if line:
                    events.append(json.loads(line))
    with open(json_path, "w") as f:
        json.dump({"events": events, "count": len(events)}, f, indent=2, ensure_ascii=False)
