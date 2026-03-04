import os
from celery import Celery
from backend.core.hyper_config import config
import logging

logger = logging.getLogger(__name__)

# Initialize the Celery application
# Connect to Redis broker and backend based on configuration
app = Celery(
    'hyper_saas',
    broker=config.REDIS_URL,
    backend=config.REDIS_URL,
    include=[
        'backend.tasks.llm_tasks',
        'backend.tasks.vision_tasks',
        'backend.tasks.jepa_tasks'
    ]
)

# Optional configuration, see the application user guide.
app.conf.update(
    task_serializer='json',
    accept_content=['json'],  # Ignore other content
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    
    # Fault Tolerance and Redis Settings
    task_reject_on_worker_lost=True,
    task_acks_late=True, # Require workers to acknowledge only AFTER execution
    broker_connection_retry_on_startup=True,
    
    # Restrict Celery from spinning up too many threads, rely on processes for CPU bounding
    worker_concurrency=config.MAX_WORKERS,
    worker_prefetch_multiplier=1, # Ensure heavy ML jobs don't get hoarded by one worker
)

logger.info(f"Celery App Initialized with Broker: {config.REDIS_URL}")
