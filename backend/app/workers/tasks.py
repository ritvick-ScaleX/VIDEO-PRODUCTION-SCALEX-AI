"""Celery tasks — async services bridged into the sync worker.

Each task opens its own async session and runs the corresponding service. The
API endpoints run these inline today; dispatching them here (``.delay(...)``)
moves the work off the request path without changing the service code.
"""
from __future__ import annotations

import asyncio
from typing import Any

from app.core.logging import get_logger
from app.database.session import AsyncSessionLocal
from app.workers.celery_app import celery_app

logger = get_logger("worker")


def _run(coro):
    """Run an async coroutine to completion inside a worker process."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


async def _analyze(product_id: str) -> dict[str, Any]:
    from app.services import analysis_service

    async with AsyncSessionLocal() as db:
        product = await analysis_service.analyze(db, product_id)
        await db.commit()
        return {"product_id": product_id, "analysis": product.analysis}


@celery_app.task(name="auralis.analyze_product")
def analyze_product_task(product_id: str) -> dict[str, Any]:
    logger.info("analyze_product_task %s", product_id)
    return _run(_analyze(product_id))


async def _scrape(product_id: str) -> dict[str, Any]:
    from app.services.product_service import _load
    from app.services.scraper_service import scrape_into_product

    async with AsyncSessionLocal() as db:
        product = await _load(db, product_id)
        data = await scrape_into_product(db, product)
        await db.commit()
        return {"product_id": product_id, "scraped": bool(data)}


@celery_app.task(name="auralis.scrape_product")
def scrape_product_task(product_id: str) -> dict[str, Any]:
    logger.info("scrape_product_task %s", product_id)
    return _run(_scrape(product_id))


@celery_app.task(name="auralis.ping")
def ping() -> str:
    return "pong"
