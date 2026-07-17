"""Image generation endpoints (prefix /products)."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.schemas.common import MessageResponse
from app.schemas.generation import (
    ImageGenerateRequest,
    ImageRead,
    ImageReviewRequest,
    SaveToggle,
)
from app.services import image_service

router = APIRouter()


@router.get("/{product_id}/images", response_model=list[ImageRead])
async def list_images(product_id: str, db: AsyncSession = Depends(get_db)):
    return await image_service.list_for_product(db, product_id)


@router.post("/{product_id}/images", response_model=list[ImageRead])
async def generate_images(product_id: str, payload: ImageGenerateRequest, db: AsyncSession = Depends(get_db)):
    return await image_service.generate(db, product_id, payload)


@router.patch("/{product_id}/images/{image_id}/review", response_model=ImageRead)
async def review_image(
    product_id: str, image_id: str, payload: ImageReviewRequest, db: AsyncSession = Depends(get_db)
):
    """Accept/reject with an optional comment — rejections steer the next generation."""
    obj = await image_service.set_review(db, image_id, payload.status, payload.comment)
    if not obj:
        raise HTTPException(status_code=404, detail="Image not found")
    return obj


@router.patch("/{product_id}/images/{image_id}/save", response_model=ImageRead)
async def save_image(product_id: str, image_id: str, payload: SaveToggle, db: AsyncSession = Depends(get_db)):
    obj = await image_service.set_saved(db, image_id, payload.is_saved)
    if not obj:
        raise HTTPException(status_code=404, detail="Image not found")
    return obj


@router.delete("/{product_id}/images/{image_id}", response_model=MessageResponse)
async def delete_image(product_id: str, image_id: str, db: AsyncSession = Depends(get_db)):
    await image_service.delete(db, image_id)
    return MessageResponse(message="Deleted")
