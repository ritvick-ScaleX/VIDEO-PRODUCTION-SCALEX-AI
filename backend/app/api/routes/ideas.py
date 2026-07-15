"""Idea endpoints — generate directions, select one (prefix /products)."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.schemas.idea import IdeaGenerateRequest, IdeaRead
from app.services import idea_service

router = APIRouter()


class StatusUpdate(BaseModel):
    status: str


@router.get("/{product_id}/ideas", response_model=list[IdeaRead])
async def list_ideas(product_id: str, db: AsyncSession = Depends(get_db)):
    return await idea_service.list_for_product(db, product_id)


@router.post("/{product_id}/ideas", response_model=list[IdeaRead])
async def generate_ideas(product_id: str, payload: IdeaGenerateRequest, db: AsyncSession = Depends(get_db)):
    return await idea_service.generate(db, product_id, payload)


@router.post("/{product_id}/ideas/{idea_id}/select", response_model=IdeaRead)
async def select_idea(product_id: str, idea_id: str, db: AsyncSession = Depends(get_db)):
    return await idea_service.select_idea(db, idea_id)


@router.patch("/{product_id}/ideas/{idea_id}", response_model=IdeaRead)
async def set_idea_status(product_id: str, idea_id: str, payload: StatusUpdate, db: AsyncSession = Depends(get_db)):
    return await idea_service.set_status(db, idea_id, payload.status)
