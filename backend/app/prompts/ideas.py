"""Idea generation — turn a user's prompt into several distinct ad directions."""
from __future__ import annotations

import json
from typing import Any

SYSTEM = (
    "You are a senior creative director. Given a brand/product brief and the "
    "user's rough idea, you propose several DISTINCT, high-impact ad concept "
    "directions — each with a clear angle and a scroll-stopping hook. Directions "
    "must be genuinely different from each other, not variations of one idea. "
    "Return only the requested JSON."
)

SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "ideas": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "title": {"type": "string"},
                    "angle": {"type": "string"},
                    "description": {"type": "string"},
                    "hook": {"type": "string"},
                },
                "required": ["title", "angle", "description", "hook"],
            },
        }
    },
    "required": ["ideas"],
}


def build_prompt(brief: dict[str, Any], user_prompt: str, count: int) -> str:
    return (
        f"Propose {count} distinct ad concept directions.\n\n"
        f"USER'S IDEA / BRIEF: {user_prompt}\n\n"
        f"BRAND & PRODUCT:\n{json.dumps(brief, indent=2, default=str)}\n\n"
        "Each idea needs: a short punchy 'title', a one-line 'angle', a 2-3 "
        "sentence 'description' of how the ad plays out, and a 'hook' (the first "
        "spoken/on-screen line). Make the directions clearly different."
    )
