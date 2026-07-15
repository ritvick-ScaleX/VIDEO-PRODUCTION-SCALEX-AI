"""AppSettings — singleton preferences for the single local user."""
from __future__ import annotations

from typing import Any

from sqlalchemy import JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base, TimestampMixin

SINGLETON_ID = "default"


class AppSettings(Base, TimestampMixin):
    __tablename__ = "settings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=SINGLETON_ID)
    theme: Mapped[str] = mapped_column(String(16), default="dark")
    language: Mapped[str] = mapped_column(String(8), default="en")
    ai_model: Mapped[str] = mapped_column(String(48), default="gpt-4o")
    storage_backend: Mapped[str] = mapped_column(String(16), default="local")
    # Default tone, formats, variation count, auto-scoring, etc.
    generation_prefs: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    meta: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
