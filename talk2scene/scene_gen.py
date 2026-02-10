"""LLM-based scene generation from transcript events."""

import json
import logging
from typing import Optional

from talk2scene.whitelist import validate_scene_event, get_whitelist

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a scene event generator for Talk2Scene.
Given transcript segments, produce one scene event per segment.

Each scene event has these fields:
- speaker_id: string
- text: the spoken text
- sta: pose code from whitelist (STA_*) — character half-body stance
- exp: expression code from whitelist (EXP_*) — facial expression overlay
- act: action code from whitelist (ACT_*) — arm/hand action overlay
- bg: background code from whitelist (BG_*) — scene background
- cg: CG illustration code from whitelist (CG_*) — full-scene illustration
- start: start timestamp in seconds
- end: end timestamp in seconds

Available codes:
{whitelist}

Rules:
- Produce exactly one scene event per transcript segment
- Normal layering order: BG -> STA -> ACT -> EXP
- CG is a full-scene illustration (like a visual novel CG). When CG is set,
  it REPLACES the entire layered scene. Use CG only for dramatic key moments.
- Only use codes from the whitelist
- If no action, use ACT_None
- If no CG illustration, use CG_None (this is the default for most events)
- Return JSON object: {{"scenes": [...]}} with an array of scene events
"""


class SceneGenerator:
    def __init__(self, model: str = "gpt-4", temperature: float = 0.3, max_tokens: int = 4096):
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self._seq_idx = 0

    def generate(self, transcript_events: list[dict]) -> list[dict]:
        try:
            import openai

            wl = get_whitelist()
            wl_text = json.dumps(wl, indent=2)

            prompt_text = ""
            for ev in transcript_events:
                prompt_text += f"[{ev.get('start', 0):.1f}s - {ev.get('end', 0):.1f}s] "
                prompt_text += f"Speaker: {ev.get('speaker_id', 'unknown')}: {ev.get('text', '')}\n"

            messages = [
                {"role": "system", "content": SYSTEM_PROMPT.format(whitelist=wl_text)},
                {"role": "user", "content": prompt_text},
            ]

            request_body = {
                "model": self.model,
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
                "messages": messages,
                "response_format": {"type": "json_object"},
            }
            logger.debug("LLM request:\n%s", json.dumps(request_body, indent=2, ensure_ascii=False))

            client = openai.OpenAI()
            resp = client.chat.completions.create(**request_body)

            raw = resp.choices[0].message.content.strip()
            usage = resp.usage
            logger.debug(
                "LLM response (model=%s, prompt_tokens=%s, completion_tokens=%s, total_tokens=%s):\n%s",
                resp.model,
                usage.prompt_tokens if usage else "?",
                usage.completion_tokens if usage else "?",
                usage.total_tokens if usage else "?",
                raw,
            )

            if raw.startswith("```"):
                raw = raw.split("\n", 1)[1].rsplit("```", 1)[0]

            parsed = json.loads(raw)
            # Handle {"scenes": [...]} wrapper (JSON mode returns root object)
            if isinstance(parsed, dict):
                # Look for array value in the object
                for key in ("scenes", "events", "data"):
                    if key in parsed and isinstance(parsed[key], list):
                        parsed = parsed[key]
                        break
                else:
                    # Single scene object
                    parsed = [parsed]
            scenes = parsed

            result = []
            for scene in scenes:
                scene["type"] = "scene"
                scene["seq"] = self._seq_idx
                self._seq_idx += 1
                validated = validate_scene_event(scene)
                result.append(validated)

            logger.debug("Validated %d scene events", len(result))
            return result

        except Exception as e:
            logger.error(f"Scene generation failed: {e}")
            return self._fallback_scenes(transcript_events)

    def _fallback_scenes(self, transcript_events: list[dict]) -> list[dict]:
        result = []
        for ev in transcript_events:
            scene = {
                "type": "scene",
                "seq": self._seq_idx,
                "speaker_id": ev.get("speaker_id", "unknown"),
                "text": ev.get("text", ""),
                "sta": "STA_Stand_Front",
                "exp": "EXP_Neutral",
                "act": "ACT_None",
                "bg": "BG_Lab_Modern",
                "cg": "CG_None",
                "start": ev.get("start", 0),
                "end": ev.get("end", 0),
            }
            self._seq_idx += 1
            result.append(scene)
        return result
