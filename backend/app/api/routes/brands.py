"""Brand CRUD + products-under-brand listing/creation."""
from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.schemas.brand import BrandCreate, BrandRead, BrandScrapeRequest, BrandUpdate
from app.schemas.common import MessageResponse
from app.schemas.product import ProductCreate, ProductRead
from app.services import brand_service, product_service

router = APIRouter()


@router.get("", response_model=list[BrandRead])
async def list_brands(db: AsyncSession = Depends(get_db)):
    return await brand_service.list_brands(db)


@router.post("", response_model=BrandRead, status_code=status.HTTP_201_CREATED)
async def create_brand(payload: BrandCreate, db: AsyncSession = Depends(get_db)):
    return await brand_service.create_brand(db, payload)


@router.post("/scrape", response_model=BrandRead, status_code=status.HTTP_201_CREATED)
async def create_brand_from_url(payload: BrandScrapeRequest, db: AsyncSession = Depends(get_db)):
    return await brand_service.create_brand_from_url(db, payload.url)


@router.get("/{brand_id}", response_model=BrandRead)
async def get_brand(brand_id: str, db: AsyncSession = Depends(get_db)):
    return await brand_service.get_brand(db, brand_id)


@router.patch("/{brand_id}", response_model=BrandRead)
async def update_brand(brand_id: str, payload: BrandUpdate, db: AsyncSession = Depends(get_db)):
    return await brand_service.update_brand(db, brand_id, payload)


@router.delete("/{brand_id}", response_model=MessageResponse)
async def delete_brand(brand_id: str, db: AsyncSession = Depends(get_db)):
    await brand_service.delete_brand(db, brand_id)
    return MessageResponse(message="Brand deleted")


@router.get("/{brand_id}/products", response_model=list[ProductRead])
async def list_products(brand_id: str, db: AsyncSession = Depends(get_db)):
    return await product_service.list_products(db, brand_id)


@router.post("/{brand_id}/products", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
async def create_product(brand_id: str, payload: ProductCreate, db: AsyncSession = Depends(get_db)):
    return await product_service.create_product(db, brand_id, payload)
