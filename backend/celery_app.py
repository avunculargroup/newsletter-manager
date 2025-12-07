from __future__ import annotations

from celery import Celery

from .app.config import get_settings

settings = get_settings()

celery_app = Celery(
    "newsletter_pipeline",
    broker=settings.redis_url,
    backend=settings.redis_url,
)
celery_app.autodiscover_tasks(["backend.app"])
