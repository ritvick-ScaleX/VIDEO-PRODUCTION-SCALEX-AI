"""Analytics endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.schemas.analytics import AnalyticsSummary
from app.services import analytics_service

router = APIRouter()


@router.get("/summary", response_model=AnalyticsSummary)
async def summary(days: int = 14, db: AsyncSession = Depends(get_db)):
    return await analytics_service.get_summary(db, days=days)
