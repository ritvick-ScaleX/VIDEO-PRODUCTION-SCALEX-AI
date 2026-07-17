"""Idea schemas — prompt -> multiple idea directions -> select one."""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from app.schemas.common import TimestampedRead


class IdeaGenerateRequest(BaseModel):
    # The user's idea / brief typed into the prompt box.
    prompt: str = Field(..., min_length=1)
    count: int = Field(default=4, ge=1, le=8)


class IdeaRead(TimestampedRead):
    product_id: str
    prompt: str | None = None
    batch_id: str | None = None
    kind: str = "video"
    title: str | None = None
    angle: str | None = None
    description: str | None = None
    hook: str | None = None
    status: str = "pending"
    meta: dict[str, Any] = {}
