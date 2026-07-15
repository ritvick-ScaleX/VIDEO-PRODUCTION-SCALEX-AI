"""Export Center endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.schemas.export import ExportCreate, ExportRead
from app.services import export_service

router = APIRouter()


@router.get("", response_model=list[ExportRead])
async def list_exports(product_id: str | None = None, db: AsyncSession = Depends(get_db)):
    return await export_service.list_exports(db, product_id)


@router.post("", response_model=ExportRead)
async def create_export(payload: ExportCreate, db: AsyncSession = Depends(get_db)):
    return await export_service.create_export(db, payload)
