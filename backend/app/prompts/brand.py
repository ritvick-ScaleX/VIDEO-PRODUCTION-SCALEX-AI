"""Derive a brand identity from a scraped homepage."""
from __future__ import annotations

import json
from typing import Any

SYSTEM = (
    "You are a brand strategist. Given the raw signals scraped from a company's "
    "website (name, tagline, description, homepage copy, colours), infer a concise, "
    "usable brand identity a creative team can apply immediately. Be specific and "
    "grounded in the signals — never invent facts about the company. Return only the "
    "requested JSON."
)

SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "name": {"type": "string"},
        "tagline": {"type": "string"},
        "mission": {"type": "string"},
        "brand_voice": {"type": "string"},
        "writing_style": {"type": "string"},
        "target_audience": {"type": "string"},
    },
    "required": [
        "name",
        "tagline",
        "mission",
        "brand_voice",
        "writing_style",
        "target_audience",
    ],
}


def build_prompt(signals: dict[str, Any]) -> str:
    return (
        "From these website signals, infer the brand identity.\n\n"
        f"SIGNALS:\n{json.dumps(signals, indent=2, default=str)}\n\n"
        "Return: a clean brand name; a short punchy tagline; a one-sentence mission; "
        "a brand_voice (tone in a phrase, e.g. 'warm, confident, a little playful'); "
        "a writing_style (concrete guidance, e.g. 'short sentences, active voice, "
        "emoji sparingly'); and the primary target_audience."
    )
