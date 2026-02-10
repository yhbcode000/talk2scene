"""Unit tests for session management."""

import json
import shutil
import tempfile
from pathlib import Path

import pytest

from talk2scene.session import SessionManager, generate_session_id


def test_generate_session_id():
    sid = generate_session_id()
    assert len(sid) > 10
    assert "_" in sid


def test_session_manager_creates_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        session = SessionManager(base_dir=tmpdir)
        assert session.session_dir.exists()
        assert (Path(tmpdir) / "sessions.jsonl").exists()


def test_session_manager_custom_id():
    with tempfile.TemporaryDirectory() as tmpdir:
        session = SessionManager(base_dir=tmpdir, session_id="test123")
        assert session.session_id == "test123"
        assert (Path(tmpdir) / "test123").exists()


def test_session_finalize():
    with tempfile.TemporaryDirectory() as tmpdir:
        session = SessionManager(base_dir=tmpdir, session_id="test_fin")
        session.finalize()
        assert session.ended_at is not None

        with open(Path(tmpdir) / "sessions.jsonl") as f:
            lines = f.readlines()
        assert len(lines) == 2  # active + ended
        last = json.loads(lines[-1])
        assert last["status"] == "ended"


def test_session_is_resumable():
    with tempfile.TemporaryDirectory() as tmpdir:
        session = SessionManager(base_dir=tmpdir, session_id="test_resume")
        assert session.is_resumable() is False

        # Create events file
        session.get_path("events.jsonl").touch()
        assert session.is_resumable() is True
