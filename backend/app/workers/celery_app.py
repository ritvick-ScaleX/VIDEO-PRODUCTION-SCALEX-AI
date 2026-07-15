"""Celery application.

Redis is both broker and result backend. Tasks live in ``app.workers.tasks``.
The API can run generations inline (works with no worker) or dispatch heavy work
here — the seam is ready for scaling scraping, analysis, and video rendering off
the request path.
"""
from __future__ import annotations

from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "auralis",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["app.workers.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    task_track_started=True,
    task_time_limit=600,
    worker_max_tasks_per_child=100,
    result_expires=3600,
)
