"""UGC Studio service (product-scoped)."""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.generation import UGCScript
from app.prompts import ugc as prompt
from app.schemas.generation import UGCGenerateRequest
from app.services import analytics_service, mocks
from app.services.ai import llm
from app.services.brief import assemble_brief
from app.services.product_service import _load


async def generate(db: AsyncSession, product_id: str, req: UGCGenerateRequest) -> UGCScript:
    product = await _load(db, product_id)
    brief = assemble_brief(product, product.brand)
    req_dict = req.model_dump()
    result = await llm.generate_structured(
        system=prompt.SYSTEM,
        prompt=prompt.build_prompt(brief, req_dict),
        schema=prompt.SCHEMA,
        mock=lambda: mocks.mock_ugc(brief, req_dict),
    )
    script = UGCScript(
        product_id=product_id,
        hook=result.get("hook"),
        script=result.get("script"),
        camera_directions=result.get("camera_directions", []),
        scene_breakdown=result.get("scene_breakdown", []),
        b_roll=result.get("b_roll", []),
        cta=result.get("cta"),
        voice_style=req.voice_style,
        emotion=req.emotion,
        audience=req.audience,
        meta={"mode": llm.mode},
    )
    db.add(script)
    await db.flush()
    await analytics_service.record_event(
        db, "ugc_generated", brand_id=product.brand_id, product_id=product_id
    )
    await db.refresh(script)
    return script


async def list_for_product(db: AsyncSession, product_id: str) -> list[UGCScript]:
    rows = await db.execute(
        select(UGCScript)
        .where(UGCScript.product_id == product_id)
        .order_by(UGCScript.created_at.desc())
    )
    return list(rows.scalars().all())


async def set_saved(db: AsyncSession, ugc_id: str, saved: bool) -> UGCScript | None:
    obj = await db.get(UGCScript, ugc_id)
    if obj:
        obj.is_saved = saved
        await db.flush()
    return obj


async def delete(db: AsyncSession, ugc_id: str) -> None:
    obj = await db.get(UGCScript, ugc_id)
    if obj:
        await db.delete(obj)
        await db.flush()
