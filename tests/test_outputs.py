"""Unit tests for output writers."""

import json
import tempfile
from pathlib import Path

import pytest

from talk2scene.outputs import OutputWriter


def test_append_event():
    with tempfile.TemporaryDirectory() as tmpdir:
        writer = OutputWriter(Path(tmpdir))
        writer.append_event({"type": "scene", "text": "hello"})
        assert writer.event_count == 1

        with open(writer.events_path) as f:
            line = f.readline().strip()
        assert json.loads(line)["text"] == "hello"


def test_append_events_bulk():
    with tempfile.TemporaryDirectory() as tmpdir:
        writer = OutputWriter(Path(tmpdir))
        events = [
            {"type": "scene", "seq": 0, "text": "a"},
            {"type": "scene", "seq": 1, "text": "b"},
        ]
        writer.append_events(events)
        assert writer.event_count == 2


def test_finalize():
    with tempfile.TemporaryDirectory() as tmpdir:
        writer = OutputWriter(Path(tmpdir))
        writer.append_event({
            "type": "scene", "seq": 0, "speaker_id": "s1",
            "text": "hello", "sta": "STA_Stand_Default",
            "exp": "EXP_Neutral", "act": "ACT_None",
            "bg": "BG_Default", "cg": "CG_None",
            "start": 0.0, "end": 1.5,
        })
        writer.finalize()

        assert writer.timeline_json.exists()
        assert writer.timeline_csv.exists()

        with open(writer.timeline_json) as f:
            snapshot = json.load(f)
        assert snapshot["event_count"] == 1

        with open(writer.timeline_csv) as f:
            lines = f.readlines()
        assert len(lines) == 2  # header + 1 row


def test_resume_count():
    with tempfile.TemporaryDirectory() as tmpdir:
        writer1 = OutputWriter(Path(tmpdir))
        writer1.append_event({"type": "scene", "text": "a"})
        writer1.append_event({"type": "scene", "text": "b"})

        # Simulate resume
        writer2 = OutputWriter(Path(tmpdir))
        assert writer2.event_count == 2
