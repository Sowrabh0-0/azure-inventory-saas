from __future__ import annotations

from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "azure_inventory",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["app.tasks.sync"],
)
celery_app.conf.update(
    timezone="UTC",
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    beat_schedule={
        "sync-all-tenants-hourly": {
            "task": "app.tasks.sync.sync_all_tenants",
            "schedule": 3600.0,
        }
    },
)
