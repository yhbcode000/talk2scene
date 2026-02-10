"""Unit tests for whitelist validation."""

import pytest
from talk2scene.whitelist import load_whitelist, validate_code, repair_code, validate_scene_event


@pytest.fixture(autouse=True)
def reset_whitelist():
    import talk2scene.whitelist as wl
    wl._whitelist = None
    load_whitelist("conf/whitelist.yaml")


def test_load_whitelist():
    wl = load_whitelist("conf/whitelist.yaml")
    assert "STA" in wl
    assert "EXP" in wl
    assert "ACT" in wl
    assert "BG" in wl
    assert "CG" in wl


def test_validate_code_valid():
    assert validate_code("STA", "STA_Stand_Front") is True
    assert validate_code("EXP", "EXP_Neutral") is True
    assert validate_code("BG", "BG_Lab_Modern") is True
    assert validate_code("CG", "CG_PandorasTech") is True
    assert validate_code("ACT", "ACT_ArmsCrossed") is True


def test_validate_code_invalid():
    assert validate_code("STA", "STA_Invalid") is False
    assert validate_code("EXP", "NOT_A_CODE") is False


def test_repair_code_valid():
    assert repair_code("STA", "STA_Stand_Front") == "STA_Stand_Front"


def test_repair_code_invalid():
    result = repair_code("STA", "STA_Invalid")
    assert result == "STA_Stand_Front"  # Falls back to first in list


def test_validate_scene_event():
    event = {
        "sta": "STA_INVALID",
        "exp": "EXP_Thinking",
        "act": "ACT_None",
        "bg": "BG_Lab_Modern",
        "cg": "CG_None",
    }
    repaired = validate_scene_event(event)
    assert repaired["sta"] == "STA_Stand_Front"  # Repaired to first valid
    assert repaired["exp"] == "EXP_Thinking"  # Kept valid


def test_cg_none_is_valid():
    assert validate_code("CG", "CG_None") is True


def test_cg_illustration_is_valid():
    assert validate_code("CG", "CG_PandorasTech") is True
