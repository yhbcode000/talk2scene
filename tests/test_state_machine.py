"""Unit tests for the state machine."""

import time

import pytest

from talk2scene.state_machine import StateManager, CharacterState


def test_character_state_defaults():
    state = CharacterState("char1")
    assert state.sta == "STA_Stand_Front"
    assert state.exp == "EXP_Neutral"


def test_character_state_custom_defaults():
    state = CharacterState("char1", {"sta": "STA_Stand_Side", "exp": "EXP_Thinking"})
    assert state.sta == "STA_Stand_Side"
    assert state.exp == "EXP_Thinking"


def test_state_manager_apply_event():
    mgr = StateManager(cooldown_ms=0)
    event = {
        "speaker_id": "char1",
        "sta": "STA_Stand_Side",
        "exp": "EXP_Laugh",
        "act": "ACT_ArmsCrossed",
        "bg": "BG_Cafe_Starbucks",
        "cg": "CG_None",
    }
    result = mgr.apply_event(event)
    assert result["state"]["sta"] == "STA_Stand_Side"
    assert result["state"]["exp"] == "EXP_Laugh"
    assert "sta" in result["changes"]


def test_state_manager_cooldown():
    mgr = StateManager(cooldown_ms=10000)  # 10s cooldown
    event1 = {"speaker_id": "char1", "sta": "STA_Stand_Side"}
    mgr.apply_event(event1)

    event2 = {"speaker_id": "char1", "sta": "STA_Stand_Lean"}
    result = mgr.apply_event(event2)
    # Should be held due to cooldown
    assert result["state"]["sta"] == "STA_Stand_Side"


def test_state_manager_multi_character():
    mgr = StateManager(cooldown_ms=0)
    ev1 = {"speaker_id": "char1", "sta": "STA_Stand_Side"}
    ev2 = {"speaker_id": "char2", "sta": "STA_Stand_Lean"}
    mgr.apply_event(ev1)
    mgr.apply_event(ev2)

    assert mgr.characters["char1"].sta == "STA_Stand_Side"
    assert mgr.characters["char2"].sta == "STA_Stand_Lean"


def test_cg_replaces_scene():
    """When CG is set, it should be stored in state (renderer handles the takeover)."""
    mgr = StateManager(cooldown_ms=0)
    event = {
        "speaker_id": "char1",
        "sta": "STA_Stand_Front",
        "exp": "EXP_Neutral",
        "cg": "CG_PandorasTech",
    }
    result = mgr.apply_event(event)
    assert result["state"]["cg"] == "CG_PandorasTech"
