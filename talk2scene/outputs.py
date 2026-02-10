"""Output writers: JSONL (primary), JSON snapshot, CSV export."""

import csv
import json
from pathlib import Path
from typing import Optional


class OutputWriter:
    def __init__(self, session_dir: Path):
        self.session_dir = session_dir
        self.events_path = session_dir / "events.jsonl"
        self.timeline_json = session_dir / "timeline.json"
        self.timeline_csv = session_dir / "timeline.csv"
        self._event_count = 0

        # Count existing events for resume
        if self.events_path.exists():
            with open(self.events_path) as f:
                self._event_count = sum(1 for _ in f)

    def append_event(self, event: dict):
        with open(self.events_path, "a") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")
            f.flush()
        self._event_count += 1

    def append_events(self, events: list[dict]):
        with open(self.events_path, "a") as f:
            for event in events:
                f.write(json.dumps(event, ensure_ascii=False) + "\n")
                self._event_count += 1
            f.flush()

    def build_json_snapshot(self):
        events = self._read_all_events()
        snapshot = {
            "event_count": len(events),
            "events": events,
        }
        with open(self.timeline_json, "w") as f:
            json.dump(snapshot, f, indent=2, ensure_ascii=False)

    def build_csv_export(self):
        events = self._read_all_events()
        scene_events = [e for e in events if e.get("type") == "scene"]
        if not scene_events:
            return

        fieldnames = ["seq", "speaker_id", "text", "sta", "exp", "act", "bg", "cg", "start", "end"]
        with open(self.timeline_csv, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(scene_events)

    def finalize(self):
        self.build_json_snapshot()
        self.build_csv_export()

    def _read_all_events(self) -> list[dict]:
        events = []
        if self.events_path.exists():
            with open(self.events_path) as f:
                for line in f:
                    line = line.strip()
                    if line:
                        events.append(json.loads(line))
        return events

    @property
    def event_count(self) -> int:
        return self._event_count
