"""Auralis backend — FastAPI application entrypoint."""
from __future__ import annotations

import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app import __version__
from app.api.router import api_router
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger("auralis")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup for the MVP (Alembic available for real migrations).
    if settings.run_migrations_on_start:
        from app.database.session import init_db

        try:
            await init_db()
            logger.info("database initialised")
        except Exception as exc:  # pragma: no cover
            logger.error("db init failed: %s", exc)
    logger.info(
        "ScaleX AI %s up — text: %s · media: %s",
        __version__,
        "live" if settings.text_ai_enabled else "mock",
        "live" if settings.google_ai_enabled else "mock",
    )
    yield


app = FastAPI(
    title="ScaleX AI API",
    version=__version__,
    description="AI Creative Studio — generate campaigns from a product.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve locally-stored generated assets.
storage_path = Path(settings.storage_dir)
storage_path.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(storage_path)), name="static")

app.include_router(api_router, prefix=settings.api_prefix)


@app.get("/health", tags=["system"])
async def health():
    return {
        "status": "ok",
        "version": __version__,
        "ai_mode": "live" if settings.text_ai_enabled else "mock",
        "text_ai": "live" if settings.text_ai_enabled else "mock",
        "media_ai": "live" if settings.google_ai_enabled else "mock",
        "text_model": settings.openai_model,
        # Confirms the Bright Data scraper fallback is configured (bool only).
        "scrape_proxy": bool(settings.scalex_browser_ws.strip() or settings.scraper_proxy_url.strip()),
    }


@app.get("/", tags=["system"])
async def root():
    return {"name": settings.app_name, "docs": "/docs", "api": settings.api_prefix}
