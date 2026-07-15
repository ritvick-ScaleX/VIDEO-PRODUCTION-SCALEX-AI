"""Brand schemas (top-level entity)."""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from app.schemas.common import TimestampedRead


class BrandScrapeRequest(BaseModel):
    url: str = Field(..., min_length=4, max_length=1024)


class BrandCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    website: str | None = None
    logo_url: str | None = None
    brand_colors: list[str] = []
    fonts: list[str] = []
    brand_voice: str | None = None
    writing_style: str | None = None
    target_audience: str | None = None
    tagline: str | None = None
    mission: str | None = None


class BrandUpdate(BaseModel):
    name: str | None = None
    website: str | None = None
    logo_url: str | None = None
    brand_colors: list[str] | None = None
    fonts: list[str] | None = None
    brand_voice: str | None = None
    writing_style: str | None = None
    target_audience: str | None = None
    tagline: str | None = None
    mission: str | None = None


class BrandRead(TimestampedRead):
    name: str
    website: str | None = None
    logo_url: str | None = None
    brand_colors: list[str] = []
    fonts: list[str] = []
    brand_voice: str | None = None
    writing_style: str | None = None
    target_audience: str | None = None
    tagline: str | None = None
    mission: str | None = None
    meta: dict[str, Any] = {}
    product_count: int = 0
