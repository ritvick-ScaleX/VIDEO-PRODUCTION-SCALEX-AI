"""Analytics — event recording + dashboard aggregation (Brand/Product model)."""
from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.analytics import AnalyticsEvent
from app.models.brand import Brand
from app.models.export import Export
from app.models.generation import GeneratedCopy, GeneratedImage, GeneratedVideo
from app.models.idea import Idea
from app.models.product import Product
from app.models.scoring import CreativeScore
from app.schemas.analytics import (
    ActivityItem,
    AnalyticsSummary,
    StatCard,
    TimeseriesPoint,
)


async def record_event(
    db: AsyncSession,
    event_type: str,
    brand_id: str | None = None,
    product_id: str | None = None,
    meta: dict[str, Any] | None = None,
) -> None:
    db.add(
        AnalyticsEvent(
            event_type=event_type,
            brand_id=brand_id,
            product_id=product_id,
            meta=meta or {},
        )
    )
    await db.flush()


async def _count(db: AsyncSession, model) -> int:
    return (await db.execute(select(func.count()).select_from(model))).scalar_one()


async def get_summary(db: AsyncSession, days: int = 14) -> AnalyticsSummary:
    brands = await _count(db, Brand)
    products = await _count(db, Product)
    ideas = await _count(db, Idea)
    images = await _count(db, GeneratedImage)
    videos = await _count(db, GeneratedVideo)
    exports = await _count(db, Export)

    stats = [
        StatCard(key="brands", label="Brands", value=brands, delta=8.0),
        StatCard(key="products", label="Products", value=products, delta=12.5),
        StatCard(key="ideas", label="Ideas", value=ideas, delta=22.0),
        StatCard(key="images", label="Images", value=images, delta=18.7),
        StatCard(key="videos", label="Videos", value=videos, delta=14.0),
        StatCard(key="exports", label="Exports", value=exports, delta=6.8),
    ]

    since = datetime.now(timezone.utc) - timedelta(days=days - 1)
    rows = (
        await db.execute(select(AnalyticsEvent).where(AnalyticsEvent.created_at >= since))
    ).scalars().all()

    key_map = {
        "product_created": "products",
        "idea_generated": "ideas",
        "image_generated": "images",
        "video_generated": "videos",
        "export_created": "exports",
        "brand_created": "brands",
    }
    buckets: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for ev in rows:
        day = ev.created_at.date().isoformat()
        k = key_map.get(ev.event_type)
        if k:
            buckets[day][k] += 1

    timeseries: list[TimeseriesPoint] = []
    for i in range(days):
        d = (since + timedelta(days=i)).date().isoformat()
        b = buckets.get(d, {})
        timeseries.append(
            TimeseriesPoint(
                date=d,
                brands=b.get("brands", 0),
                products=b.get("products", 0),
                ideas=b.get("ideas", 0),
                images=b.get("images", 0),
                videos=b.get("videos", 0),
                exports=b.get("exports", 0),
            )
        )

    recent = (
        await db.execute(
            select(AnalyticsEvent).order_by(AnalyticsEvent.created_at.desc()).limit(12)
        )
    ).scalars().all()
    activity = [ActivityItem.model_validate(e) for e in recent]

    platform_rows = (
        await db.execute(
            select(GeneratedCopy.platform, func.count()).group_by(GeneratedCopy.platform)
        )
    ).all()
    platform_breakdown = {p: c for p, c in platform_rows}

    avg_score = (await db.execute(select(func.avg(CreativeScore.overall)))).scalar()

    return AnalyticsSummary(
        stats=stats,
        timeseries=timeseries,
        activity=activity,
        platform_breakdown=platform_breakdown,
        avg_score=round(float(avg_score or 0), 1),
    )
