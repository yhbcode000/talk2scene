"""Performance monitoring and reporting."""

import json
import time
from collections import defaultdict
from pathlib import Path


class PerformanceMonitor:
    def __init__(self):
        self.timers: dict[str, list[float]] = defaultdict(list)
        self._active: dict[str, float] = {}

    def start(self, name: str):
        self._active[name] = time.time()

    def stop(self, name: str) -> float:
        if name not in self._active:
            return 0.0
        elapsed = time.time() - self._active.pop(name)
        self.timers[name].append(elapsed)
        return elapsed

    def record(self, name: str, value: float):
        self.timers[name].append(value)

    def report(self) -> dict:
        result = {}
        for name, values in self.timers.items():
            result[name] = {
                "count": len(values),
                "total_s": round(sum(values), 3),
                "avg_s": round(sum(values) / len(values), 3) if values else 0,
                "min_s": round(min(values), 3) if values else 0,
                "max_s": round(max(values), 3) if values else 0,
            }
        return result

    def save(self, path: Path):
        with open(path, "w") as f:
            json.dump(self.report(), f, indent=2)
