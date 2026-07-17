"""Video storyboard + script generation prompts."""
from __future__ import annotations

import json
from typing import Any

SYSTEM = (
    "You are a short-form video director and scriptwriter. You turn a product "
    "brief into a shootable storyboard: scene-by-scene visuals, voiceover, "
    "on-screen text, and transitions, paced to the requested duration. Return "
    "only the requested JSON."
)

SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "script": {"type": "string"},
        "voiceover": {"type": "string"},
        "character": {"type": "string"},
        "setting": {"type": "string"},
        "storyboard": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "scene": {"type": "string"},
                    "visual": {"type": "string"},
                    "voiceover": {"type": "string"},
                    "on_screen_text": {"type": "string"},
                    "duration": {"type": "string"},
                },
                "required": ["scene", "visual", "voiceover", "on_screen_text", "duration"],
            },
        },
        "captions": {"type": "array", "items": {"type": "string"}},
        "transitions": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["script", "voiceover", "character", "setting", "storyboard", "captions", "transitions"],
}

_DURATION_HINT = {
    "15s": "15 seconds, 3-4 fast scenes",
    "30s": "30 seconds, 4-6 scenes",
    "60s": "60 seconds, 6-8 scenes",
    "reel": "~25 seconds vertical Reel, punchy",
    "short": "~30 seconds vertical Short, hook-first",
    "story": "~15 seconds vertical Story, single message",
}


def build_prompt(brief: dict[str, Any], req: dict[str, Any]) -> str:
    duration = req.get("duration", "30s")
    return (
        f"Create a video storyboard and script. Target: {_DURATION_HINT.get(duration, duration)}.\n"
        f"FORMAT: {req.get('format', 'reel')}\n"
        f"EXTRA: {req.get('instructions') or 'n/a'}\n\n"
        f"BRAND & PRODUCT BRIEF:\n{json.dumps(brief, indent=2, default=str)}\n\n"
        "Deliver: a full script; a single voiceover track; a storyboard where each "
        "scene has visual, voiceover, on_screen_text, and duration; per-scene "
        "captions; and a list of transitions between scenes."
    )
