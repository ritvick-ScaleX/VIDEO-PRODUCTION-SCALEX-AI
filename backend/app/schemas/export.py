"""Export schemas."""
from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel

from app.schemas.common import TimestampedRead


class ExportCreate(BaseModel):
    product_id: str | None = None
    kind: Literal["png", "jpg", "mp4", "pdf", "zip"] = "pdf"
    label: str | None = None
    asset_ids: list[str] = []


class ExportRead(TimestampedRead):
    product_id: str | None = None
    kind: str
    label: str
    url: str
    size_bytes: int
    meta: dict[str, Any] = {}
