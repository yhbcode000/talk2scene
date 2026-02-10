"""Audio input: batch file loading and Redis stream consumer."""

import io
import logging
import struct
import wave
from pathlib import Path
from typing import Iterator, Optional

logger = logging.getLogger(__name__)


def normalize_audio(input_path: str, output_path: str, sample_rate: int = 16000) -> str:
    from pydub import AudioSegment

    audio = AudioSegment.from_file(input_path)
    audio = audio.set_frame_rate(sample_rate).set_channels(1).set_sample_width(2)
    audio.export(output_path, format="wav")
    logger.info(f"Normalized audio: {input_path} -> {output_path}")
    return output_path


def load_batch_audio(audio_path: str, output_dir: str, sample_rate: int = 16000) -> str:
    p = Path(audio_path)
    if not p.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")
    out = str(Path(output_dir) / "audio_normalized.wav")
    return normalize_audio(audio_path, out, sample_rate)


class RedisAudioConsumer:
    def __init__(self, cfg):
        import redis

        self.client = redis.Redis(
            host=cfg.redis.host,
            port=cfg.redis.port,
            db=cfg.redis.db,
        )
        self.stream_key = cfg.redis.stream_key
        self.stt_stream_key = cfg.redis.stt_stream_key
        self.group = cfg.redis.consumer_group
        self.consumer = cfg.redis.consumer_name
        self.block_ms = cfg.redis.block_ms
        self.batch_size = cfg.redis.batch_size
        self.backpressure_max = cfg.redis.backpressure_max
        self._ensure_group()

    def _ensure_group(self):
        for key in (self.stream_key, self.stt_stream_key):
            try:
                self.client.xgroup_create(key, self.group, id="0", mkstream=True)
            except Exception:
                pass  # Group may already exist

    def consume(self) -> Iterator[tuple[str, str, dict]]:
        """Yield (msg_id, stream_name, data_dict) from both STT and mic streams.

        STT stream is checked alongside mic; both are read in a single
        xreadgroup call so the Redis server decides ordering.
        """
        while True:
            # Backpressure check on both streams
            backpressured = False
            for key in (self.stream_key, self.stt_stream_key):
                info = self.client.xpending(key, self.group)
                if info["pending"] >= self.backpressure_max:
                    logger.warning(
                        "Backpressure: too many pending on %s (%d), waiting...",
                        key, info["pending"],
                    )
                    backpressured = True
            if backpressured:
                import time
                time.sleep(1)
                continue

            entries = self.client.xreadgroup(
                self.group,
                self.consumer,
                {self.stt_stream_key: ">", self.stream_key: ">"},
                count=self.batch_size,
                block=self.block_ms,
            )
            if not entries:
                continue

            for stream_name_raw, messages in entries:
                stream_name = (
                    stream_name_raw.decode()
                    if isinstance(stream_name_raw, bytes)
                    else stream_name_raw
                )
                for msg_id, data in messages:
                    mid = msg_id.decode() if isinstance(msg_id, bytes) else msg_id
                    yield mid, stream_name, data
                    self.client.xack(stream_name, self.group, msg_id)

    def close(self):
        self.client.close()


def chunks_to_wav(chunks: list[bytes], sample_rate: int = 16000) -> bytes:
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        for chunk in chunks:
            wf.writeframes(chunk)
    return buf.getvalue()
