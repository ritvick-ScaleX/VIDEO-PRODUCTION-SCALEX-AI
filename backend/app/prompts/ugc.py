"""UGC creator-script generation prompts."""
from __future__ import annotations

import json
from typing import Any

SYSTEM = (
    "You are a UGC creative director who scripts high-converting user-generated "
    "content for short-form social video. You write natural, authentic creator "
    "dialogue, precise camera and shot directions, and a tight scene plan that a "
    "creator could film today on a phone. Return only the requested JSON."
)

SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "hook": {"type": "string"},
        "script": {"type": "string"},
        "camera_directions": {"type": "array", "items": {"type": "string"}},
        "scene_breakdown": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "scene": {"type": "string"},
                    "action": {"type": "string"},
                    "dialogue": {"type": "string"},
                    "duration": {"type": "string"},
                },
                "required": ["scene", "action", "dialogue", "duration"],
            },
        },
        "b_roll": {"type": "array", "items": {"type": "string"}},
        "cta": {"type": "string"},
    },
    "required": ["hook", "script", "camera_directions", "scene_breakdown", "b_roll", "cta"],
}


def build_prompt(brief: dict[str, Any], req: dict[str, Any]) -> str:
    return (
        "Write a complete UGC creator script for a short-form video.\n\n"
        f"VOICE STYLE: {req.get('voice_style', 'authentic')}\n"
        f"EMOTION: {req.get('emotion', 'excited')}\n"
        f"AUDIENCE: {req.get('audience') or brief.get('target_audience', 'general')}\n"
        f"EXTRA: {req.get('instructions') or 'n/a'}\n\n"
        f"BRAND & PRODUCT BRIEF:\n{json.dumps(brief, indent=2, default=str)}\n\n"
        "Deliver: a scroll-stopping spoken hook; the full spoken script; "
        "camera_directions (framing/movement per beat); a scene_breakdown with "
        "scene, action, dialogue, and duration; b_roll shot ideas; and a spoken CTA."
    )
