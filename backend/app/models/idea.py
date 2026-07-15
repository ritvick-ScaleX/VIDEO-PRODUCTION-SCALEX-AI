"""Idea — AI-generated creative directions for a product.

You write a prompt; the AI proposes several ideas. You SELECT one (status
`selected`); the rest stay `pending`. The selected idea seeds the script.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin, uuid_str

if TYPE_CHECKING:
    from app.models.product import Product


class Idea(Base, TimestampMixin):
    __tablename__ = "ideas"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    product_id: Mapped[str] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"), index=True
    )
    # The user's prompt/brief that produced this batch of ideas.
    prompt: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Groups ideas generated together (one prompt -> one batch).
    batch_id: Mapped[str | None] = mapped_column(String(36), index=True, nullable=True)

    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    angle: Mapped[str | None] = mapped_column(String(120), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    hook: Mapped[str | None] = mapped_column(Text, nullable=True)
    # pending | selected | rejected
    status: Mapped[str] = mapped_column(String(16), default="pending", index=True)
    meta: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)

    product: Mapped["Product"] = relationship(back_populates="ideas")
