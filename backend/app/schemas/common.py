"""Shared schema base classes and helpers."""
from __future__ import annotations

from datetime import datetime
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class ORMModel(BaseModel):
    """Base for read models mapped from ORM instances."""

    model_config = ConfigDict(from_attributes=True)


class TimestampedRead(ORMModel):
    id: str
    created_at: datetime
    updated_at: datetime


class MessageResponse(BaseModel):
    message: str
    ok: bool = True


class Page(BaseModel, Generic[T]):
    items: list[T]
    total: int
