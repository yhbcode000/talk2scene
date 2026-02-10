"""Session management for Talk2Scene."""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional


def generate_session_id() -> str:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    short = uuid.uuid4().hex[:8]
    return f"{ts}_{short}"


class SessionManager:
    def __init__(self, base_dir: str = "output", session_id: Optional[str] = None):
        self.session_id = session_id or generate_session_id()
        self.base_dir = Path(base_dir)
        self.session_dir = self.base_dir / self.session_id
        self.session_dir.mkdir(parents=True, exist_ok=True)
        self.registry_path = self.base_dir / "sessions.jsonl"
        self.started_at = datetime.now().isoformat()
        self.ended_at: Optional[str] = None
        self._register()

    def _register(self):
        entry = {
            "session_id": self.session_id,
            "started_at": self.started_at,
            "status": "active",
        }
        with open(self.registry_path, "a") as f:
            f.write(json.dumps(entry) + "\n")

    def get_path(self, filename: str) -> Path:
        return self.session_dir / filename

    def finalize(self):
        self.ended_at = datetime.now().isoformat()
        entry = {
            "session_id": self.session_id,
            "ended_at": self.ended_at,
            "status": "ended",
        }
        with open(self.registry_path, "a") as f:
            f.write(json.dumps(entry) + "\n")

    def is_resumable(self) -> bool:
        return self.get_path("events.jsonl").exists()
