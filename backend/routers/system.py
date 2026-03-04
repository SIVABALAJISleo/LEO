import psutil
import logging
import time
from fastapi import APIRouter, Response, Request
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Dict, Any
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST, Gauge, Histogram, Counter

from backend.celery_app import app as celery_app
from backend.core.middleware import redis_client

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/system", tags=["System"])

# Define Prometheus Metrics Definitions
SYSTEM_CPU_USAGE = Gauge('hyper_system_cpu_usage_percent', 'Current CPU usage percent')
SYSTEM_MEM_USAGE = Gauge('hyper_system_mem_usage_percent', 'Current Memory usage percent')
ACTIVE_WORKERS = Gauge('hyper_active_celery_workers', 'Number of active Celery workers available')

REQUEST_LATENCY = Histogram('hyper_api_request_latency_seconds', 'Request latency in seconds', ['method', 'endpoint'])
REQUEST_COUNT = Counter('hyper_api_request_count', 'Total API requests', ['method', 'endpoint', 'http_status'])

class PrometheusMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # We only record high-level endpoints to avoid cardinality explosion on random paths
        endpoint = request.url.path
        
        try:
            response = await call_next(request)
            status_code = response.status_code
        except Exception as e:
            status_code = 500
            REQUEST_COUNT.labels(method=request.method, endpoint=endpoint, http_status=status_code).inc()
            raise e
            
        process_time = time.time() - start_time
        REQUEST_LATENCY.labels(method=request.method, endpoint=endpoint).observe(process_time)
        REQUEST_COUNT.labels(method=request.method, endpoint=endpoint, http_status=status_code).inc()
        
        return response

@router.get("/health")
async def system_health() -> Dict[str, Any]:
    """
    Complete Cluster Health Check
    Used by Kubernetes / Docker Swarm or Load Balancers.
    """
    health_status = {"status": "healthy", "components": {}}
    
    # 1. Check Redis
    try:
        if redis_client and redis_client.ping():
            health_status["components"]["redis"] = "online"
        else:
            health_status["components"]["redis"] = "offline"
            health_status["status"] = "degraded"
    except Exception as e:
        health_status["components"]["redis"] = f"error: {e}"
        health_status["status"] = "degraded"
        
    # 2. Check Celery Workers (Ping via Broker)
    try:
        i = celery_app.control.inspect()
        active_workers = i.active() if i else None
        
        if active_workers is not None:
            worker_count = len(active_workers)
            health_status["components"]["celery_workers"] = f"online ({worker_count} active nodes)"
            ACTIVE_WORKERS.set(worker_count)
            if worker_count == 0:
                 health_status["status"] = "degraded"
        else:
            health_status["components"]["celery_workers"] = "offline"
            health_status["status"] = "degraded"
            ACTIVE_WORKERS.set(0)
    except Exception as e:
         health_status["components"]["celery_workers"] = f"error: {e}"
         health_status["status"] = "degraded"
         ACTIVE_WORKERS.set(0)
         
    # 3. Host Node Telemetry
    cpu_usage = psutil.cpu_percent(interval=None)
    mem_usage = psutil.virtual_memory().percent
    
    health_status["telemetry"] = {
        "cpu_usage_percent": cpu_usage,
        "memory_usage_percent": mem_usage
    }
    
    SYSTEM_CPU_USAGE.set(cpu_usage)
    SYSTEM_MEM_USAGE.set(mem_usage)
    
    return health_status

@router.get("/metrics")
async def system_metrics():
    """
    Exposes metrics in Prometheus format for Grafana Dashboards.
    """
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
