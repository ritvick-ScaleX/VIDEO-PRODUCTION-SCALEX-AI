"""UGC Studio endpoints (prefix /products)."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.schemas.common import MessageResponse
from app.schemas.generation import SaveToggle, UGCGenerateRequest, UGCRead
from app.services import ugc_service

router = APIRouter()


@router.get("/{product_id}/ugc", response_model=list[UGCRead])
async def list_ugc(product_id: str, db: AsyncSession = Depends(get_db)):
    return await ugc_service.list_for_product(db, product_id)


@router.post("/{product_id}/ugc", response_model=UGCRead)
async def generate_ugc(product_id: str, payload: UGCGenerateRequest, db: AsyncSession = Depends(get_db)):
    return await ugc_service.generate(db, product_id, payload)


@router.patch("/{product_id}/ugc/{ugc_id}/save", response_model=UGCRead)
async def save_ugc(product_id: str, ugc_id: str, payload: SaveToggle, db: AsyncSession = Depends(get_db)):
    obj = await ugc_service.set_saved(db, ugc_id, payload.is_saved)
    if not obj:
        raise HTTPException(status_code=404, detail="UGC script not found")
    return obj


@router.delete("/{product_id}/ugc/{ugc_id}", response_model=MessageResponse)
async def delete_ugc(product_id: str, ugc_id: str, db: AsyncSession = Depends(get_db)):
    await ugc_service.delete(db, ugc_id)
    return MessageResponse(message="Deleted")
