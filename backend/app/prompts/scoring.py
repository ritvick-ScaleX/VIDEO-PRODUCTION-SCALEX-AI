"""Creative scoring prompts."""
from __future__ import annotations

import json
from typing import Any

SYSTEM = (
    "You are a conversion-rate-optimization expert who grades marketing creative "
    "like a strict but fair judge. You score 0-100 on each dimension, justify with "
    "a short summary, and give concrete, actionable improvement suggestions. Be "
    "calibrated — reserve 90+ for genuinely excellent work. Return only the JSON."
)

SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "overall": {"type": "number"},
        "hook_strength": {"type": "integer"},
        "readability": {"type": "integer"},
        "brand_consistency": {"type": "integer"},
        "visual_hierarchy": {"type": "integer"},
        "cta_quality": {"type": "integer"},
        "emotion": {"type": "integer"},
        "conversion_potential": {"type": "integer"},
        "suggestions": {"type": "array", "items": {"type": "string"}},
        "summary": {"type": "string"},
    },
    "required": [
        "overall", "hook_strength", "readability", "brand_consistency",
        "visual_hierarchy", "cta_quality", "emotion", "conversion_potential",
        "suggestions", "summary",
    ],
}


def build_prompt(target_type: str, content: str, brand: dict[str, Any]) -> str:
    return (
        f"Score this {target_type} creative for a marketing campaign.\n\n"
        f"CREATIVE:\n{content}\n\n"
        f"BRAND CONTEXT:\n{json.dumps(brand, indent=2, default=str)}\n\n"
        "Score 0-100 on: hook_strength, readability, brand_consistency, "
        "visual_hierarchy, cta_quality, emotion, conversion_potential. "
        "Set 'overall' to the weighted average. Give 3-5 concrete 'suggestions' "
        "and a 2-3 sentence 'summary'."
    )
