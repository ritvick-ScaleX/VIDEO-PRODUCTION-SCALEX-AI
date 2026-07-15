"""Idea service — generate directions from a prompt, then select one."""
from __future__ import annotations

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.base import uuid_str
from app.models.idea import Idea
from app.prompts import ideas as prompt
from app.schemas.idea import IdeaGenerateRequest
from app.services import analytics_service, mocks
from app.services.ai import llm
from app.services.brief import assemble_brief
from app.services.product_service import _load


async def generate(db: AsyncSession, product_id: str, req: IdeaGenerateRequest) -> list[Idea]:
    product = await _load(db, product_id)
    brief = assemble_brief(product, product.brand)

    result = await llm.generate_structured(
        system=prompt.SYSTEM,
        prompt=prompt.build_prompt(brief, req.prompt, req.count),
        schema=prompt.SCHEMA,
        mock=lambda: mocks.mock_ideas(brief, req.prompt, req.count),
        thinking=True,
        effort="medium",
    )
    batch = uuid_str()
    created: list[Idea] = []
    for item in result.get("ideas", [])[: req.count]:
        idea = Idea(
            product_id=product_id,
            prompt=req.prompt,
            batch_id=batch,
            title=item.get("title"),
            angle=item.get("angle"),
            description=item.get("description"),
            hook=item.get("hook"),
            status="pending",
        )
        db.add(idea)
        created.append(idea)
    await db.flush()
    await analytics_service.record_event(
        db, "idea_generated", brand_id=product.brand_id, product_id=product_id,
        meta={"count": len(created)},
    )
    for i in created:
        await db.refresh(i)
    return created


async def list_for_product(db: AsyncSession, product_id: str) -> list[Idea]:
    rows = await db.execute(
        select(Idea).where(Idea.product_id == product_id).order_by(Idea.created_at.desc())
    )
    return list(rows.scalars().all())


async def select_idea(db: AsyncSession, idea_id: str) -> Idea:
    idea = await db.get(Idea, idea_id)
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")
    # Only one selected per product; the rest stay pending.
    rows = await db.execute(
        select(Idea).where(Idea.product_id == idea.product_id, Idea.status == "selected")
    )
    for other in rows.scalars().all():
        if other.id != idea.id:
            other.status = "pending"
    idea.status = "selected"
    await db.flush()
    await analytics_service.record_event(
        db, "idea_selected", product_id=idea.product_id, meta={"idea_id": idea.id}
    )
    await db.refresh(idea)
    return idea


async def set_status(db: AsyncSession, idea_id: str, status: str) -> Idea:
    idea = await db.get(Idea, idea_id)
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")
    idea.status = status
    await db.flush()
    await db.refresh(idea)
    return idea
