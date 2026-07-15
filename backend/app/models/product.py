"""Product — belongs to a Brand. Merges the old Project + ProductData.

Carries the scraped/entered facts, the AI marketing analysis, and owns all the
generated creative (images, ideas, videos, copy, scores).
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin, uuid_str

if TYPE_CHECKING:
    from app.models.brand import Brand
    from app.models.generation import (
        GeneratedCopy,
        GeneratedImage,
        GeneratedVideo,
        UGCScript,
    )
    from app.models.idea import Idea
    from app.models.scoring import CreativeScore


class Product(Base, TimestampMixin):
    __tablename__ = "products"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    brand_id: Mapped[str] = mapped_column(
        ForeignKey("brands.id", ondelete="CASCADE"), index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    source_type: Mapped[str] = mapped_column(String(16), default="manual")  # url | manual
    source_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    status: Mapped[str] = mapped_column(String(24), default="draft", index=True)

    # ---- Product facts ----
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    features: Mapped[list[str]] = mapped_column(JSON, default=list)
    benefits: Mapped[list[str]] = mapped_column(JSON, default=list)
    price: Mapped[str | None] = mapped_column(String(120), nullable=True)
    target_audience: Mapped[str | None] = mapped_column(Text, nullable=True)
    cta: Mapped[str | None] = mapped_column(String(255), nullable=True)
    images: Mapped[list[str]] = mapped_column(JSON, default=list)  # scraped image URLs
    selected_images: Mapped[list[str]] = mapped_column(JSON, default=list)  # curated subset AI uses
    logo_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    brand_colors: Mapped[list[str]] = mapped_column(JSON, default=list)
    hero_content: Mapped[str | None] = mapped_column(Text, nullable=True)
    reviews: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list)
    faqs: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list)
    thumbnail_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)

    raw_scrape: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    analysis: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)

    brand: Mapped["Brand"] = relationship(back_populates="products")
    images_rel: Mapped[list["GeneratedImage"]] = relationship(
        back_populates="product", cascade="all, delete-orphan"
    )
    videos: Mapped[list["GeneratedVideo"]] = relationship(
        back_populates="product", cascade="all, delete-orphan"
    )
    ideas: Mapped[list["Idea"]] = relationship(
        back_populates="product", cascade="all, delete-orphan"
    )
    copies: Mapped[list["GeneratedCopy"]] = relationship(
        back_populates="product", cascade="all, delete-orphan"
    )
    ugc_scripts: Mapped[list["UGCScript"]] = relationship(
        back_populates="product", cascade="all, delete-orphan"
    )
    scores: Mapped[list["CreativeScore"]] = relationship(
        back_populates="product", cascade="all, delete-orphan"
    )
