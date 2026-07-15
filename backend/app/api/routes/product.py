"""Product data, AI analysis, and re-scrape endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.schemas.product import AnalysisUpdate, ProductDataRead, ProductDataUpdate
from app.services import analysis_service, scraper_service
from app.services.project_service import _load

router = APIRouter()


@router.get("/{project_id}/product", response_model=ProductDataRead)
async def get_product(project_id: str, db: AsyncSession = Depends(get_db)):
    project = await _load(db, project_id)
    if not project.product:
        raise HTTPException(status_code=404, detail="No product data")
    return project.product


@router.patch("/{project_id}/product", response_model=ProductDataRead)
async def update_product(
    project_id: str, payload: ProductDataUpdate, db: AsyncSession = Depends(get_db)
):
    project = await _load(db, project_id)
    product = project.product
    if not product:
        raise HTTPException(status_code=404, detail="No product data")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(product, field, value)
    await db.flush()
    await db.refresh(product)
    return product


@router.post("/{project_id}/analyze", response_model=ProductDataRead)
async def analyze_product(project_id: str, db: AsyncSession = Depends(get_db)):
    return await analysis_service.analyze(db, project_id)


@router.patch("/{project_id}/analysis", response_model=ProductDataRead)
async def update_analysis(
    project_id: str, payload: AnalysisUpdate, db: AsyncSession = Depends(get_db)
):
    return await analysis_service.update_analysis(db, project_id, payload.analysis)


@router.post("/{project_id}/rescrape", response_model=ProductDataRead)
async def rescrape(project_id: str, db: AsyncSession = Depends(get_db)):
    project = await _load(db, project_id)
    if not project.source_url:
        raise HTTPException(status_code=400, detail="Project has no source URL")
    try:
        await scraper_service.scrape_into_project(
            db, project, project.product, project.brand
        )
    except Exception:
        # Site blocked us (bot protection) or was unreachable — keep existing
        # data so the user can edit manually instead of erroring out.
        raise HTTPException(
            status_code=422,
            detail="Couldn't fetch this URL (the site likely blocks automated access). Enter the product details manually in the Product tab.",
        )
    await db.refresh(project.product)
    return project.product
