"""AnalyticsEvent — lightweight event log powering the analytics dashboard."""
from __future__ import annotations

from typing import Any

from sqlalchemy import JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base, TimestampMixin, uuid_str


class AnalyticsEvent(Base, TimestampMixin):
    __tablename__ = "analytics_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    brand_id: Mapped[str | None] = mapped_column(String(36), index=True, nullable=True)
    product_id: Mapped[str | None] = mapped_column(String(36), index=True, nullable=True)
    # brand_created | product_created | idea_generated | idea_selected |
    # image_generated | video_generated | frames_generated | copy_generated |
    # export_created | scored | scrape_completed ...
    event_type: Mapped[str] = mapped_column(String(48), index=True)
    meta: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
