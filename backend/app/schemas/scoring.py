"""Creative scoring schemas."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel

from app.schemas.common import TimestampedRead


class ScoreRequest(BaseModel):
    target_type: Literal["copy", "image", "video", "ugc"] = "copy"
    target_id: str | None = None
    # Free-form text to score if not referencing a stored asset.
    text: str | None = None


class ScoreRead(TimestampedRead):
    product_id: str
    target_type: str
    target_id: str | None = None
    overall: float
    hook_strength: int
    readability: int
    brand_consistency: int
    visual_hierarchy: int
    cta_quality: int
    emotion: int
    conversion_potential: int
    suggestions: list[str] = []
    summary: str | None = None
