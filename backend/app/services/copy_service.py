"""AI Copy generation service (product-scoped)."""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.generation import GeneratedCopy
from app.prompts import copy as prompt
from app.schemas.generation import CopyGenerateRequest
from app.services import analytics_service, mocks
from app.services.ai import llm
from app.services.brief import assemble_brief
from app.services.product_service import _load


async def generate(db: AsyncSession, product_id: str, req: CopyGenerateRequest) -> GeneratedCopy:
    product = await _load(db, product_id)
    brief = assemble_brief(product, product.brand)
    result = await llm.generate_structured(
        system=prompt.SYSTEM,
        prompt=prompt.build_prompt(brief, req.platform, req.tone, req.variations, req.instructions),
        schema=prompt.SCHEMA,
        mock=lambda: mocks.mock_copy(brief, req.platform, req.tone, req.variations),
    )
    variations = result.get("variations", [])
    primary = variations[0] if variations else {}
    copy = GeneratedCopy(
        product_id=product_id,
        platform=req.platform,
        tone=req.tone,
        headline=primary.get("headline"),
        body=primary.get("body"),
        cta=primary.get("cta"),
        variations=variations,
        meta={"mode": llm.mode, "angle": primary.get("angle")},
    )
    db.add(copy)
    await db.flush()
    await analytics_service.record_event(
        db, "copy_generated", brand_id=product.brand_id, product_id=product_id,
        meta={"platform": req.platform, "tone": req.tone},
    )
    await db.refresh(copy)
    return copy


async def list_for_product(db: AsyncSession, product_id: str) -> list[GeneratedCopy]:
    rows = await db.execute(
        select(GeneratedCopy)
        .where(GeneratedCopy.product_id == product_id)
        .order_by(GeneratedCopy.created_at.desc())
    )
    return list(rows.scalars().all())


async def set_saved(db: AsyncSession, copy_id: str, saved: bool) -> GeneratedCopy | None:
    obj = await db.get(GeneratedCopy, copy_id)
    if obj:
        obj.is_saved = saved
        await db.flush()
    return obj


async def delete(db: AsyncSession, copy_id: str) -> None:
    obj = await db.get(GeneratedCopy, copy_id)
    if obj:
        await db.delete(obj)
        await db.flush()
