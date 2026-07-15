"""Product schemas (merged product facts + AI analysis, under a Brand)."""
from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

from app.schemas.common import TimestampedRead


class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    source_type: Literal["url", "manual"] = "manual"
    source_url: str | None = None
    # Seed facts when entering manually.
    description: str | None = None
    features: list[str] | None = None
    benefits: list[str] | None = None
    price: str | None = None
    target_audience: str | None = None
    cta: str | None = None


class ProductUpdate(BaseModel):
    brand_id: str | None = None  # reassign the product to another brand
    name: str | None = None
    description: str | None = None
    features: list[str] | None = None
    benefits: list[str] | None = None
    price: str | None = None
    target_audience: str | None = None
    cta: str | None = None
    images: list[str] | None = None
    selected_images: list[str] | None = None
    logo_url: str | None = None
    brand_colors: list[str] | None = None
    hero_content: str | None = None
    status: str | None = None


class ProductRead(TimestampedRead):
    brand_id: str
    name: str
    source_type: str
    source_url: str | None = None
    status: str
    description: str | None = None
    features: list[str] = []
    benefits: list[str] = []
    price: str | None = None
    target_audience: str | None = None
    cta: str | None = None
    images: list[str] = []
    selected_images: list[str] = []
    logo_url: str | None = None
    brand_colors: list[str] = []
    hero_content: str | None = None
    reviews: list[dict[str, Any]] = []
    faqs: list[dict[str, Any]] = []
    thumbnail_url: str | None = None
    raw_scrape: dict[str, Any] = {}
    analysis: dict[str, Any] = {}


class AnalysisUpdate(BaseModel):
    analysis: dict[str, Any]
