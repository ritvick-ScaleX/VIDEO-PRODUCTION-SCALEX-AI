"""CreativeScore — quality analysis for a generated asset (under a Product)."""
from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import JSON, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin, uuid_str

if TYPE_CHECKING:
    from app.models.product import Product


class CreativeScore(Base, TimestampMixin):
    __tablename__ = "creative_scores"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    product_id: Mapped[str] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"), index=True
    )
    target_type: Mapped[str] = mapped_column(String(16), default="copy")
    target_id: Mapped[str | None] = mapped_column(String(36), nullable=True)

    overall: Mapped[float] = mapped_column(Float, default=0)
    hook_strength: Mapped[int] = mapped_column(Integer, default=0)
    readability: Mapped[int] = mapped_column(Integer, default=0)
    brand_consistency: Mapped[int] = mapped_column(Integer, default=0)
    visual_hierarchy: Mapped[int] = mapped_column(Integer, default=0)
    cta_quality: Mapped[int] = mapped_column(Integer, default=0)
    emotion: Mapped[int] = mapped_column(Integer, default=0)
    conversion_potential: Mapped[int] = mapped_column(Integer, default=0)

    suggestions: Mapped[list[str]] = mapped_column(JSON, default=list)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)

    product: Mapped["Product"] = relationship(back_populates="scores")
