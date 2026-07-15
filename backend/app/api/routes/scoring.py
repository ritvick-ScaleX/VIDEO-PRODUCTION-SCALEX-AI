"""Creative scoring endpoints (prefix /products)."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.schemas.scoring import ScoreRead, ScoreRequest
from app.services import scoring_service

router = APIRouter()


@router.get("/{product_id}/scores", response_model=list[ScoreRead])
async def list_scores(product_id: str, db: AsyncSession = Depends(get_db)):
    return await scoring_service.list_for_product(db, product_id)


@router.post("/{product_id}/score", response_model=ScoreRead)
async def score(product_id: str, payload: ScoreRequest, db: AsyncSession = Depends(get_db)):
    return await scoring_service.score(db, product_id, payload)
