"""Copy generation endpoints (prefix /products)."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.schemas.common import MessageResponse
from app.schemas.generation import CopyGenerateRequest, CopyRead, SaveToggle
from app.services import copy_service

router = APIRouter()


@router.get("/{product_id}/copy", response_model=list[CopyRead])
async def list_copy(product_id: str, db: AsyncSession = Depends(get_db)):
    return await copy_service.list_for_product(db, product_id)


@router.post("/{product_id}/copy", response_model=CopyRead)
async def generate_copy(product_id: str, payload: CopyGenerateRequest, db: AsyncSession = Depends(get_db)):
    return await copy_service.generate(db, product_id, payload)


@router.patch("/{product_id}/copy/{copy_id}/save", response_model=CopyRead)
async def save_copy(product_id: str, copy_id: str, payload: SaveToggle, db: AsyncSession = Depends(get_db)):
    obj = await copy_service.set_saved(db, copy_id, payload.is_saved)
    if not obj:
        raise HTTPException(status_code=404, detail="Copy not found")
    return obj


@router.delete("/{product_id}/copy/{copy_id}", response_model=MessageResponse)
async def delete_copy(product_id: str, copy_id: str, db: AsyncSession = Depends(get_db)):
    await copy_service.delete(db, copy_id)
    return MessageResponse(message="Deleted")
