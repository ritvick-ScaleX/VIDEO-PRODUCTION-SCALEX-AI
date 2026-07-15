"""Creative Scoring service (product-scoped)."""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.generation import (
    GeneratedCopy,
    GeneratedImage,
    GeneratedVideo,
    UGCScript,
)
from app.models.scoring import CreativeScore
from app.prompts import scoring as prompt
from app.schemas.scoring import ScoreRequest
from app.services import analytics_service, mocks
from app.services.ai import llm
from app.services.brief import brand_context
from app.services.product_service import _load


async def _content_for(db: AsyncSession, req: ScoreRequest) -> str:
    if req.text:
        return req.text
    if not req.target_id:
        return ""
    if req.target_type == "copy":
        c = await db.get(GeneratedCopy, req.target_id)
        return "\n".join(filter(None, [c.headline, c.body, c.cta])) if c else ""
    if req.target_type == "ugc":
        u = await db.get(UGCScript, req.target_id)
        return "\n".join(filter(None, [u.hook, u.script, u.cta])) if u else ""
    if req.target_type == "video":
        v = await db.get(GeneratedVideo, req.target_id)
        return "\n".join(filter(None, [v.script, v.voiceover])) if v else ""
    if req.target_type == "image":
        i = await db.get(GeneratedImage, req.target_id)
        return (i.prompt or "") if i else ""
    return ""


async def score(db: AsyncSession, product_id: str, req: ScoreRequest) -> CreativeScore:
    product = await _load(db, product_id)
    content = await _content_for(db, req)
    ctx = brand_context(product.brand, product)
    result = await llm.generate_structured(
        system=prompt.SYSTEM,
        prompt=prompt.build_prompt(req.target_type, content or "(no content)", ctx),
        schema=prompt.SCHEMA,
        mock=lambda: mocks.mock_score(req.target_type, content),
        thinking=True,
        effort="medium",
    )
    entry = CreativeScore(
        product_id=product_id,
        target_type=req.target_type,
        target_id=req.target_id,
        overall=float(result.get("overall", 0)),
        hook_strength=int(result.get("hook_strength", 0)),
        readability=int(result.get("readability", 0)),
        brand_consistency=int(result.get("brand_consistency", 0)),
        visual_hierarchy=int(result.get("visual_hierarchy", 0)),
        cta_quality=int(result.get("cta_quality", 0)),
        emotion=int(result.get("emotion", 0)),
        conversion_potential=int(result.get("conversion_potential", 0)),
        suggestions=result.get("suggestions", []),
        summary=result.get("summary"),
    )
    db.add(entry)
    await db.flush()
    await analytics_service.record_event(
        db, "scored", brand_id=product.brand_id, product_id=product_id,
        meta={"target_type": req.target_type, "overall": entry.overall},
    )
    await db.refresh(entry)
    return entry


async def list_for_product(db: AsyncSession, product_id: str) -> list[CreativeScore]:
    rows = await db.execute(
        select(CreativeScore)
        .where(CreativeScore.product_id == product_id)
        .order_by(CreativeScore.created_at.desc())
    )
    return list(rows.scalars().all())
