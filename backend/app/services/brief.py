"""Assemble a compact brand+product brief that every generator feeds on.

Brand identity (voice, colors, audience, tagline) is merged with the product's
facts and AI analysis into one dict the prompts consume.
"""
from __future__ import annotations

from typing import Any

from app.models.brand import Brand
from app.models.product import Product


def assemble_brief(product: Product | None, brand: Brand | None) -> dict[str, Any]:
    p = product
    b = brand
    analysis = (p.analysis if p and p.analysis else {}) or {}
    brief: dict[str, Any] = {
        "brand_name": b.name if b else None,
        "product_name": (p.name if p else None) or "the product",
        "description": p.description if p else None,
        "features": (p.features if p else []) or [],
        "benefits": (p.benefits if p else []) or analysis.get("benefits", []),
        "price": p.price if p else None,
        "cta": (p.cta if p else None) or (analysis.get("cta_suggestions") or [None])[0],
        "target_audience": (
            (b.target_audience if b else None)
            or (p.target_audience if p else None)
            or analysis.get("customer_persona")
        ),
        # --- Brand identity ---
        "brand_voice": (b.brand_voice if b else None) or analysis.get("brand_voice"),
        "writing_style": b.writing_style if b else None,
        "brand_colors": (b.brand_colors if b else None) or (p.brand_colors if p else []),
        "tagline": b.tagline if b else None,
        "mission": b.mission if b else None,
        # --- Analysis ---
        "usp": analysis.get("usp"),
        "pain_points": analysis.get("pain_points", []),
        "marketing_angles": analysis.get("marketing_angles", []),
        "hooks": analysis.get("hooks", []),
        "emotional_triggers": analysis.get("emotional_triggers", []),
    }
    return {k: v for k, v in brief.items() if v not in (None, [], "")}


def brand_context(brand: Brand | None, product: Product | None) -> dict[str, Any]:
    return {
        "brand_name": brand.name if brand else None,
        "brand_voice": brand.brand_voice if brand else None,
        "target_audience": (brand.target_audience if brand else None)
        or (product.target_audience if product else None),
        "tagline": brand.tagline if brand else None,
        "product_name": product.name if product else None,
    }
