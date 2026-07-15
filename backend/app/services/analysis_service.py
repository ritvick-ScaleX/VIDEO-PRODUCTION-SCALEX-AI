"""AI Product Analysis service (product-scoped)."""
from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product import Product
from app.prompts import analysis as prompt
from app.services import analytics_service, mocks
from app.services.ai import llm
from app.services.product_service import _load


async def analyze(db: AsyncSession, product_id: str) -> Product:
    product = await _load(db, product_id)
    payload = {
        "product_name": product.name,
        "description": product.description,
        "features": product.features,
        "benefits": product.benefits,
        "price": product.price,
        "target_audience": product.target_audience,
        "hero_content": product.hero_content,
        "reviews": product.reviews,
    }
    result = await llm.generate_structured(
        system=prompt.SYSTEM,
        prompt=prompt.build_prompt(payload),
        schema=prompt.SCHEMA,
        mock=lambda: mocks.mock_analysis(payload),
        thinking=True,
        effort="high",
    )
    product.analysis = result
    product.status = "ready"
    await db.flush()
    await analytics_service.record_event(
        db, "analysis_completed", brand_id=product.brand_id, product_id=product_id
    )
    await db.refresh(product)
    return product


async def update_analysis(db: AsyncSession, product_id: str, analysis: dict) -> Product:
    product = await _load(db, product_id)
    product.analysis = analysis
    await db.flush()
    await db.refresh(product)
    return product
