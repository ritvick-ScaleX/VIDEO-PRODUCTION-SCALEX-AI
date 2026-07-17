"""Product detail, analysis, and re-scrape (prefix /products)."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.schemas.common import MessageResponse
from app.schemas.product import AnalysisUpdate, ProductRead, ProductUpdate
from app.services import analysis_service, product_service, scraper_service

router = APIRouter()


@router.get("/{product_id}", response_model=ProductRead)
async def get_product(product_id: str, db: AsyncSession = Depends(get_db)):
    return await product_service.get_product(db, product_id)


@router.patch("/{product_id}", response_model=ProductRead)
async def update_product(product_id: str, payload: ProductUpdate, db: AsyncSession = Depends(get_db)):
    return await product_service.update_product(db, product_id, payload)


@router.delete("/{product_id}", response_model=MessageResponse)
async def delete_product(product_id: str, db: AsyncSession = Depends(get_db)):
    await product_service.delete_product(db, product_id)
    return MessageResponse(message="Product deleted")


@router.post("/{product_id}/analyze", response_model=ProductRead)
async def analyze_product(product_id: str, db: AsyncSession = Depends(get_db)):
    return await analysis_service.analyze(db, product_id)


@router.patch("/{product_id}/analysis", response_model=ProductRead)
async def update_analysis(product_id: str, payload: AnalysisUpdate, db: AsyncSession = Depends(get_db)):
    return await analysis_service.update_analysis(db, product_id, payload.analysis)


@router.post("/{product_id}/rescrape", response_model=ProductRead)
async def rescrape(product_id: str, db: AsyncSession = Depends(get_db)):
    product = await product_service.get_product(db, product_id)
    if not product.source_url:
        raise HTTPException(status_code=400, detail="Product has no source URL")
    try:
        await scraper_service.scrape_into_product(db, product)
    except Exception:
        raise HTTPException(
            status_code=422,
            detail="Couldn't fetch this URL (the site likely blocks automated access). Enter details manually.",
        )
    # Fresh data → fresh analysis, automatically.
    try:
        await analysis_service.analyze(db, product_id)
    except Exception:
        pass  # keep the refreshed data even if analysis hiccups
    return await product_service.get_product(db, product_id)
