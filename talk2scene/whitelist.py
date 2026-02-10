"""Whitelist validation for scene component codes."""

from pathlib import Path
from typing import Optional

import yaml


_whitelist: Optional[dict] = None


def load_whitelist(path: str = "conf/whitelist.yaml") -> dict:
    global _whitelist
    with open(path, "r") as f:
        _whitelist = yaml.safe_load(f)
    return _whitelist


def get_whitelist() -> dict:
    if _whitelist is None:
        return load_whitelist()
    return _whitelist


def validate_code(category: str, code: str) -> bool:
    wl = get_whitelist()
    return code in wl.get(category, [])


def repair_code(category: str, code: str) -> str:
    wl = get_whitelist()
    codes = wl.get(category, [])
    if code in codes:
        return code
    # Return default (first) code for the category
    if codes:
        return codes[0]
    raise ValueError(f"No whitelist entries for category {category}")


def validate_scene_event(event: dict) -> dict:
    repaired = dict(event)
    for cat in ["sta", "exp", "act", "bg", "cg"]:
        key = cat.upper()
        if cat in repaired:
            repaired[cat] = repair_code(key, repaired[cat])
    return repaired
