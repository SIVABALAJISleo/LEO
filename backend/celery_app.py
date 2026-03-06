import os
from celery import Celery
from backend.core.hyper_config import config
import logging
import os
import sentry_sdk
from sentry_sdk.integrations.celery import CeleryIntegration

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.celery import CeleryInstrumentor

OTEL_ENDPOINT = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://jaeger:4318/v1/traces")
resource = Resource(attributes={"service.name": "hyper-celery-worker"})
trace.set_tracer_provider(TracerProvider(resource=resource))
otlp_exporter = OTLPSpanExporter(endpoint=OTEL_ENDPOINT)
trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(otlp_exporter))

CeleryInstrumentor().instrument()
import sentry_sdk
from sentry_sdk.integrations.celery import CeleryIntegration

logger = logging.getLogger(__name__)

SENTRY_DSN = os.getenv("SENTRY_DSN", "")
if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[CeleryIntegration()],
        traces_sample_rate=1.0
    )

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
    
    # DLQ (Dead Letter Queue) routing for unprocessable tasks
    task_routes={
        'backend.tasks.*': {'queue': 'celery'},
    },
    task_default_queue='celery',
    task_create_missing_queues=True,
    
    # Restrict Celery from spinning up too many threads, rely on processes for CPU bounding
    worker_concurrency=config.MAX_WORKERS,
    worker_prefetch_multiplier=1, # Ensure heavy ML jobs don't get hoarded by one worker
)

logger.info(f"Celery App Initialized with Broker: {config.REDIS_URL}")
