"""Brand — the top-level entity. One brand owns many products.

Holds the brand identity (logo, colors, fonts, voice) that flows into every
generation for its products.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin, uuid_str

if TYPE_CHECKING:
    from app.models.product import Product


class Brand(Base, TimestampMixin):
    __tablename__ = "brands"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    website: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    logo_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    brand_colors: Mapped[list[str]] = mapped_column(JSON, default=list)
    fonts: Mapped[list[str]] = mapped_column(JSON, default=list)
    brand_voice: Mapped[str | None] = mapped_column(Text, nullable=True)
    writing_style: Mapped[str | None] = mapped_column(Text, nullable=True)
    target_audience: Mapped[str | None] = mapped_column(Text, nullable=True)
    tagline: Mapped[str | None] = mapped_column(String(512), nullable=True)
    mission: Mapped[str | None] = mapped_column(Text, nullable=True)
    meta: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)

    products: Mapped[list["Product"]] = relationship(
        back_populates="brand", cascade="all, delete-orphan"
    )
