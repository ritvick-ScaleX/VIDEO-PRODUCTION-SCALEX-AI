"""Product lifecycle — under a Brand. Create (optional scrape), read, update, delete."""
from __future__ import annotations

import uuid

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.logging import get_logger
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate
from app.services import analytics_service, brand_service
from app.storage import storage

logger = get_logger(__name__)

_SEED_FIELDS = {
    "description", "features", "benefits", "ingredients", "price", "target_audience", "cta",
}


async def _load(db: AsyncSession, product_id: str) -> Product:
    result = await db.execute(
        select(Product).options(selectinload(Product.brand)).where(Product.id == product_id)
    )
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


async def list_products(db: AsyncSession, brand_id: str) -> list[Product]:
    result = await db.execute(
        select(Product)
        .where(Product.brand_id == brand_id)
        .order_by(Product.created_at.desc())
    )
    return list(result.scalars().all())


async def get_product(db: AsyncSession, product_id: str) -> Product:
    return await _load(db, product_id)


async def create_product(db: AsyncSession, brand_id: str, data: ProductCreate) -> Product:
    await brand_service._load(db, brand_id)  # validate brand exists
    seed = {k: v for k, v in data.model_dump().items() if k in _SEED_FIELDS and v is not None}
    product = Product(
        brand_id=brand_id,
        name=data.name,
        source_type=data.source_type,
        source_url=data.source_url,
        status="scraping" if data.source_type == "url" else "ready",
        **seed,
    )
    db.add(product)
    await db.flush()
    await analytics_service.record_event(
        db, "product_created", brand_id=brand_id, product_id=product.id,
        meta={"source_type": data.source_type},
    )

    if data.source_type == "url" and data.source_url:
        from app.services import analysis_service, scraper_service

        try:
            await scraper_service.scrape_into_product(db, product)
        except Exception as exc:
            logger.warning("scrape failed for %s: %s", data.source_url, exc)
        # Auto-analyze right after import — the studio opens fully briefed
        # (ingredients, angles, audience) with no manual "Analyze" step.
        try:
            product.status = "analyzing"
            await db.flush()
            await analysis_service.analyze(db, product.id)
        except Exception as exc:
            logger.warning("auto-analysis failed for %s: %s", product.id, exc)
        product.status = "ready"

    await db.flush()
    return await _load(db, product.id)


async def update_product(db: AsyncSession, product_id: str, data: ProductUpdate) -> Product:
    product = await _load(db, product_id)
    payload = data.model_dump(exclude_unset=True)
    if payload.get("brand_id"):
        await brand_service._load(db, payload["brand_id"])  # 404 if target brand is missing
    for field, value in payload.items():
        setattr(product, field, value)
    await db.flush()
    return await _load(db, product_id)


async def delete_product(db: AsyncSession, product_id: str) -> None:
    product = await _load(db, product_id)
    await db.delete(product)
    await db.flush()


_IMG_EXT = {"png", "jpg", "jpeg", "webp", "gif"}


async def add_uploaded_images(
    db: AsyncSession, product_id: str, files: list[tuple[bytes, str]]
) -> Product:
    """Store uploaded image bytes and append their URLs to the product's images.

    A reliable manual fallback when a site blocks server-side scraping.
    """
    product = await _load(db, product_id)
    imgs = list(product.images or [])
    for data, filename in files:
        if not data:
            continue
        ext = (filename.rsplit(".", 1)[-1].lower() if "." in (filename or "") else "png")
        if ext not in _IMG_EXT:
            ext = "png"
        key = f"products/{product_id}/uploads/{uuid.uuid4().hex[:10]}.{ext}"
        url = storage.save_bytes(key, data)
        if url and url not in imgs:
            imgs.append(url)
    product.images = imgs[:50]
    if not product.thumbnail_url and product.images:
        product.thumbnail_url = product.images[0]
    await db.flush()
    return await _load(db, product_id)


async def add_image_urls(db: AsyncSession, product_id: str, urls: list[str]) -> Product:
    """Append pasted image URL(s) to the product's images."""
    product = await _load(db, product_id)
    imgs = list(product.images or [])
    for raw in urls:
        u = (raw or "").strip()
        if u and u not in imgs:
            imgs.append(u)
    product.images = imgs[:50]
    if not product.thumbnail_url and product.images:
        product.thumbnail_url = product.images[0]
    await db.flush()
    return await _load(db, product_id)
