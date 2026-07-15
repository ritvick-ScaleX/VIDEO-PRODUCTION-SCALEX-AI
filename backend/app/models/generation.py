"""Generated creative assets: images, videos, copy, UGC — all under a Product."""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON, Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin, uuid_str

if TYPE_CHECKING:
    from app.models.product import Product


class GeneratedImage(Base, TimestampMixin):
    __tablename__ = "generated_images"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    product_id: Mapped[str] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"), index=True
    )
    # white_background | creative | product_shot | frame
    category: Mapped[str] = mapped_column(String(24), default="creative", index=True)
    format: Mapped[str] = mapped_column(String(24), default="square")
    prompt: Mapped[str | None] = mapped_column(Text, nullable=True)
    url: Mapped[str] = mapped_column(String(1024))
    width: Mapped[int] = mapped_column(Integer, default=1024)
    height: Mapped[int] = mapped_column(Integer, default=1024)
    meta: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    is_saved: Mapped[bool] = mapped_column(Boolean, default=False)

    product: Mapped["Product"] = relationship(back_populates="images_rel")


class GeneratedVideo(Base, TimestampMixin):
    __tablename__ = "generated_videos"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    product_id: Mapped[str] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"), index=True
    )
    # The selected idea this video is built from (nullable for ad-hoc videos).
    idea_id: Mapped[str | None] = mapped_column(
        ForeignKey("ideas.id", ondelete="SET NULL"), nullable=True
    )
    duration: Mapped[str] = mapped_column(String(16), default="reel")
    format: Mapped[str] = mapped_column(String(24), default="reel")
    script: Mapped[str | None] = mapped_column(Text, nullable=True)
    storyboard: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list)
    voiceover: Mapped[str | None] = mapped_column(Text, nullable=True)
    captions: Mapped[list[str]] = mapped_column(JSON, default=list)
    transitions: Mapped[list[str]] = mapped_column(JSON, default=list)
    # Storyboard FRAME image URLs, generated before the video render.
    frame_urls: Mapped[list[str]] = mapped_column(JSON, default=list)
    thumbnail_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    video_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    # draft | frames_ready | rendering | ready | error
    status: Mapped[str] = mapped_column(String(16), default="draft")
    progress: Mapped[int] = mapped_column(Integer, default=0)
    meta: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    is_saved: Mapped[bool] = mapped_column(Boolean, default=False)

    product: Mapped["Product"] = relationship(back_populates="videos")


class GeneratedCopy(Base, TimestampMixin):
    __tablename__ = "generated_copy"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    product_id: Mapped[str] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"), index=True
    )
    platform: Mapped[str] = mapped_column(String(32), index=True)
    tone: Mapped[str] = mapped_column(String(24), default="professional")
    headline: Mapped[str | None] = mapped_column(String(512), nullable=True)
    body: Mapped[str | None] = mapped_column(Text, nullable=True)
    cta: Mapped[str | None] = mapped_column(String(255), nullable=True)
    variations: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list)
    meta: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    is_saved: Mapped[bool] = mapped_column(Boolean, default=False)

    product: Mapped["Product"] = relationship(back_populates="copies")


class UGCScript(Base, TimestampMixin):
    __tablename__ = "ugc_scripts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    product_id: Mapped[str] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"), index=True
    )
    hook: Mapped[str | None] = mapped_column(Text, nullable=True)
    script: Mapped[str | None] = mapped_column(Text, nullable=True)
    camera_directions: Mapped[list[str]] = mapped_column(JSON, default=list)
    scene_breakdown: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list)
    b_roll: Mapped[list[str]] = mapped_column(JSON, default=list)
    cta: Mapped[str | None] = mapped_column(String(512), nullable=True)
    voice_style: Mapped[str | None] = mapped_column(String(64), nullable=True)
    emotion: Mapped[str | None] = mapped_column(String(64), nullable=True)
    audience: Mapped[str | None] = mapped_column(String(255), nullable=True)
    meta: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    is_saved: Mapped[bool] = mapped_column(Boolean, default=False)

    product: Mapped["Product"] = relationship(back_populates="ugc_scripts")
