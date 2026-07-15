"""Top-level API router — Brand -> Product -> creative generators."""
from __future__ import annotations

from fastapi import APIRouter

from app.api.routes import (
    analytics,
    brands,
    copy,
    exports,
    ideas,
    images,
    products,
    scoring,
    settings,
    ugc,
    videos,
)

api_router = APIRouter()

# Brands (+ products under a brand)
api_router.include_router(brands.router, prefix="/brands", tags=["brands"])

# Product detail + product-scoped generators
api_router.include_router(products.router, prefix="/products", tags=["products"])
api_router.include_router(ideas.router, prefix="/products", tags=["ideas"])
api_router.include_router(copy.router, prefix="/products", tags=["copy"])
api_router.include_router(images.router, prefix="/products", tags=["images"])
api_router.include_router(videos.router, prefix="/products", tags=["videos"])
api_router.include_router(ugc.router, prefix="/products", tags=["ugc"])
api_router.include_router(scoring.router, prefix="/products", tags=["scoring"])

# Cross-cutting
api_router.include_router(exports.router, prefix="/exports", tags=["exports"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(settings.router, prefix="/settings", tags=["settings"])
