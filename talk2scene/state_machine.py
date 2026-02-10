"""Per-character state machine with transition smoothing."""

import time
from typing import Optional


class CharacterState:
    def __init__(self, character_id: str, defaults: Optional[dict] = None):
        self.character_id = character_id
        defaults = defaults or {}
        self.sta = defaults.get("sta", "STA_Stand_Front")
        self.exp = defaults.get("exp", "EXP_Neutral")
        self.act = defaults.get("act", "ACT_None")
        self.bg = defaults.get("bg", "BG_Lab_Modern")
        self.cg = defaults.get("cg", "CG_None")
        self.last_transition_time = 0.0
        self.hold_count = 0

    def to_dict(self) -> dict:
        return {
            "character_id": self.character_id,
            "sta": self.sta,
            "exp": self.exp,
            "act": self.act,
            "bg": self.bg,
            "cg": self.cg,
        }


class StateManager:
    def __init__(self, cooldown_ms: float = 500, hold_frames: int = 3, fade_ms: float = 200):
        self.characters: dict[str, CharacterState] = {}
        self.cooldown_s = cooldown_ms / 1000.0
        self.hold_frames = hold_frames
        self.fade_ms = fade_ms

    def get_or_create(self, character_id: str, defaults: Optional[dict] = None) -> CharacterState:
        if character_id not in self.characters:
            self.characters[character_id] = CharacterState(character_id, defaults)
        return self.characters[character_id]

    def apply_event(self, event: dict) -> dict:
        char_id = event.get("speaker_id", "default")
        state = self.get_or_create(char_id)

        now = time.time()
        elapsed = now - state.last_transition_time

        transition_event = {"type": "transition", "character_id": char_id, "changes": {}}

        if elapsed >= self.cooldown_s:
            for field in ("sta", "exp", "act", "bg", "cg"):
                new_val = event.get(field)
                if new_val and new_val != getattr(state, field):
                    transition_event["changes"][field] = {
                        "from": getattr(state, field),
                        "to": new_val,
                        "fade_ms": self.fade_ms,
                    }
                    setattr(state, field, new_val)

            if transition_event["changes"]:
                state.last_transition_time = now
                state.hold_count = 0
        else:
            state.hold_count += 1

        transition_event["state"] = state.to_dict()
        return transition_event
