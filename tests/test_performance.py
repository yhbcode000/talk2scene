"""Unit tests for performance monitoring."""

import tempfile
import json
from pathlib import Path

from talk2scene.performance import PerformanceMonitor


def test_start_stop():
    mon = PerformanceMonitor()
    mon.start("test_op")
    import time
    time.sleep(0.01)
    elapsed = mon.stop("test_op")
    assert elapsed > 0


def test_record():
    mon = PerformanceMonitor()
    mon.record("custom", 1.5)
    mon.record("custom", 2.5)
    report = mon.report()
    assert report["custom"]["count"] == 2
    assert report["custom"]["total_s"] == 4.0


def test_report():
    mon = PerformanceMonitor()
    mon.record("op_a", 1.0)
    mon.record("op_a", 3.0)
    report = mon.report()
    assert report["op_a"]["avg_s"] == 2.0
    assert report["op_a"]["min_s"] == 1.0
    assert report["op_a"]["max_s"] == 3.0


def test_save():
    mon = PerformanceMonitor()
    mon.record("test", 1.0)
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "perf.json"
        mon.save(path)
        with open(path) as f:
            data = json.load(f)
        assert "test" in data
