"""Brand service — top-level CRUD."""
from __future__ import annotations

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.brand import Brand
from app.models.product import Product
from app.schemas.brand import BrandCreate, BrandUpdate
from app.services import analytics_service


async def _load(db: AsyncSession, brand_id: str) -> Brand:
    brand = await db.get(Brand, brand_id)
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")
    return brand


async def _with_counts(db: AsyncSession, brands: list[Brand]) -> list[dict]:
    if not brands:
        return []
    rows = await db.execute(
        select(Product.brand_id, func.count()).group_by(Product.brand_id)
    )
    counts = {bid: c for bid, c in rows.all()}
    out = []
    for b in brands:
        d = {c.name: getattr(b, c.name) for c in Brand.__table__.columns}
        d["product_count"] = counts.get(b.id, 0)
        out.append(d)
    return out


async def list_brands(db: AsyncSession) -> list[dict]:
    result = await db.execute(select(Brand).order_by(Brand.created_at.desc()))
    return await _with_counts(db, list(result.scalars().all()))


async def get_brand(db: AsyncSession, brand_id: str) -> dict:
    brand = await _load(db, brand_id)
    return (await _with_counts(db, [brand]))[0]


async def create_brand(db: AsyncSession, data: BrandCreate) -> dict:
    brand = Brand(**data.model_dump(exclude_none=True))
    db.add(brand)
    await db.flush()
    await analytics_service.record_event(db, "brand_created", brand_id=brand.id)
    return (await _with_counts(db, [brand]))[0]


async def create_brand_from_url(db: AsyncSession, url: str) -> dict:
    """Create a brand by scraping its website (name, logo, colours, voice auto-filled).

    Degrades gracefully: if the scrape fails, a bare brand (with a name derived from
    the hostname) is still created so the user can fill in the rest manually.
    """
    from urllib.parse import urlparse

    from app.core.logging import get_logger
    from app.services import scraper_service

    logger = get_logger(__name__)
    host = (urlparse(url).netloc or url).replace("www.", "")
    fallback_name = host.split(".")[0].title() if host else "New brand"

    brand = Brand(name="New brand", website=url)
    db.add(brand)
    await db.flush()
    try:
        await scraper_service.scrape_into_brand(db, brand)
    except Exception as exc:  # keep the brand even if the scrape fails
        logger.warning("brand scrape failed for %s: %s", url, exc)
        if not brand.name or brand.name == "New brand":
            brand.name = fallback_name
        meta = dict(brand.meta or {})
        meta["scrape_error"] = str(exc)
        brand.meta = meta
        await db.flush()
    await analytics_service.record_event(db, "brand_created", brand_id=brand.id, meta={"from_url": True})
    await db.refresh(brand)  # reload all columns in-context (scrape expired some)
    return (await _with_counts(db, [brand]))[0]


async def update_brand(db: AsyncSession, brand_id: str, data: BrandUpdate) -> dict:
    brand = await _load(db, brand_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(brand, field, value)
    await db.flush()
    return (await _with_counts(db, [brand]))[0]


async def delete_brand(db: AsyncSession, brand_id: str) -> None:
    brand = await _load(db, brand_id)
    await db.delete(brand)
    await db.flush()
