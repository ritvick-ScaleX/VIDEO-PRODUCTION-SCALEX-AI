"""Market angles — Meta-ads creative directions for images AND videos."""
from __future__ import annotations

import json
from typing import Any

SYSTEM = (
    "You are a senior Meta (Facebook/Instagram) performance-creative strategist. "
    "You design scroll-stopping ad concepts that convert in-feed: thumb-stopping "
    "in the first second, one clear angle each, native to Meta placements "
    "(feed 1:1/4:5, Reels/Stories 9:16). Given a product brief and the user's "
    "rough direction, propose DISTINCT concepts of two kinds:\n"
    "• kind='image' — a single static ad image concept: a concrete, art-directable "
    "scene built around the product and its world (e.g. sunscreen → golden-hour "
    "beach flat-lay with sand and water splash). Describe exactly what's in frame.\n"
    "• kind='video' — a short-form video ad concept (Reel): the narrative arc, "
    "presenter, and payoff.\n"
    "Concepts must be genuinely different from each other — different angles, "
    "settings and emotional triggers, not variations of one idea. Ground every "
    "concept in the product's real facts (ingredients, benefits, audience). "
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
                    "kind": {"type": "string", "enum": ["image", "video"]},
                    "title": {"type": "string"},
                    "angle": {"type": "string"},
                    "description": {"type": "string"},
                    "hook": {"type": "string"},
                },
                "required": ["kind", "title", "angle", "description", "hook"],
            },
        }
    },
    "required": ["ideas"],
}


def build_prompt(brief: dict[str, Any], user_prompt: str, count: int) -> str:
    n_img = max(1, count // 2)
    n_vid = max(1, count - n_img)
    return (
        f"Propose exactly {n_img} image ad concepts (kind='image') and "
        f"{n_vid} video ad concepts (kind='video') for Meta ads.\n\n"
        f"USER'S DIRECTION: {user_prompt}\n\n"
        f"BRAND & PRODUCT:\n{json.dumps(brief, indent=2, default=str)}\n\n"
        "Each concept needs: 'kind'; a short punchy 'title'; a one-line 'angle' "
        "(the selling angle, e.g. pain-to-solution, ingredient-hero, social proof); "
        "a 2-3 sentence 'description' — for images, the exact scene to shoot "
        "(setting, props, light, where the product sits, mood); for videos, how "
        "the ad plays out beat by beat; and a 'hook' (first line / headline). "
        "Make every concept feel native to Meta feed & Reels, not like a TV ad."
    )
