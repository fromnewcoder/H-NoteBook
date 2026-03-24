from celery import Celery

from app.config import settings

celery_app = Celery(
    "hnb_workers",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["app.workers.indexing_tasks", "app.workers.export_tasks"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour max
    worker_prefetch_multiplier=1,
    broker_connection_retry_on_startup=True,
)
