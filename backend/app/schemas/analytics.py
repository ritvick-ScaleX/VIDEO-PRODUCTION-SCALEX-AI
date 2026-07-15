"""Analytics schemas — dashboard summary + activity feed."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from app.schemas.common import ORMModel


class StatCard(BaseModel):
    key: str
    label: str
    value: int
    delta: float = 0.0  # % change vs previous period


class TimeseriesPoint(BaseModel):
    date: str
    brands: int = 0
    products: int = 0
    ideas: int = 0
    images: int = 0
    videos: int = 0
    exports: int = 0


class ActivityItem(ORMModel):
    id: str
    brand_id: str | None = None
    product_id: str | None = None
    event_type: str
    meta: dict = {}
    created_at: datetime


class AnalyticsSummary(BaseModel):
    stats: list[StatCard]
    timeseries: list[TimeseriesPoint]
    activity: list[ActivityItem]
    platform_breakdown: dict[str, int] = {}
    avg_score: float = 0.0
