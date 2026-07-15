"""Export — a downloadable artifact produced from generated creative."""
from __future__ import annotations

from typing import Any

from sqlalchemy import JSON, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base, TimestampMixin, uuid_str


class Export(Base, TimestampMixin):
    __tablename__ = "exports"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    product_id: Mapped[str | None] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"), index=True, nullable=True
    )
    # png | jpg | mp4 | pdf | zip
    kind: Mapped[str] = mapped_column(String(8), index=True)
    label: Mapped[str] = mapped_column(String(255))
    url: Mapped[str] = mapped_column(String(1024))
    size_bytes: Mapped[int] = mapped_column(Integer, default=0)
    meta: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
