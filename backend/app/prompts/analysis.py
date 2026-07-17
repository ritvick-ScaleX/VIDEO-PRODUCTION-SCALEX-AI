"""AI Product Analysis — turn raw product facts into a marketing brief."""
from __future__ import annotations

import json
from typing import Any

SYSTEM = (
    "You are a world-class direct-response marketing strategist and brand analyst. "
    "You reverse-engineer what makes a product sell: who it's for, what pain it "
    "removes, the emotional triggers that move that buyer, and the sharpest angles "
    "to sell it. You are concrete and specific — never generic. Return only the "
    "requested JSON."
)

SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "brand_voice": {"type": "string"},
        "customer_persona": {"type": "string"},
        "pain_points": {"type": "array", "items": {"type": "string"}},
        "benefits": {"type": "array", "items": {"type": "string"}},
        "marketing_angles": {"type": "array", "items": {"type": "string"}},
        "offers": {"type": "array", "items": {"type": "string"}},
        "hooks": {"type": "array", "items": {"type": "string"}},
        "cta_suggestions": {"type": "array", "items": {"type": "string"}},
        "emotional_triggers": {"type": "array", "items": {"type": "string"}},
        "ingredients": {"type": "array", "items": {"type": "string"}},
        "usp": {"type": "string"},
        "strategy_summary": {"type": "string"},
    },
    "required": [
        "brand_voice", "customer_persona", "pain_points", "benefits",
        "marketing_angles", "offers", "hooks", "cta_suggestions",
        "emotional_triggers", "ingredients", "usp", "strategy_summary",
    ],
}


def build_prompt(product: dict[str, Any]) -> str:
    return (
        "Analyse this product and produce a marketing brief.\n\n"
        f"PRODUCT DATA:\n{json.dumps(product, indent=2, default=str)}\n\n"
        "Deliver:\n"
        "- brand_voice: one crisp sentence describing the voice to write in.\n"
        "- customer_persona: a vivid 2-3 sentence portrait of the ideal buyer.\n"
        "- pain_points: 4-6 specific frustrations this buyer feels today.\n"
        "- benefits: 4-6 outcome-focused benefits (not features).\n"
        "- marketing_angles: 4-6 distinct angles to sell from.\n"
        "- offers: 3-4 compelling offer ideas.\n"
        "- hooks: 5-7 scroll-stopping opening lines.\n"
        "- cta_suggestions: 4-6 punchy calls to action.\n"
        "- emotional_triggers: 4-6 emotions to activate.\n"
        "- ingredients: IF this is an ingredient-led product (skincare, cosmetics, "
        "food, supplements, cleaning…), list the key ingredients/actives found in the "
        "product data (e.g. 'Vitamin C', 'SPF 50', 'Niacinamide'). If ingredients "
        "don't apply to this product type (apparel, electronics…), return [].\n"
        "- usp: one sentence unique selling proposition.\n"
        "- strategy_summary: a 3-4 sentence go-to-market summary."
    )
