from celery import Celery
from app.settings import settings
from kombu import Queue

celery_app = Celery(
    "kleo_tasks",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

# If necessary, configure other Celery options, but you don’t need to run the worker here.
celery_app.conf.task_queues = (
    Queue("activity-classification"),
    Queue("activity-classification-new"),
    Queue("default"),
)
