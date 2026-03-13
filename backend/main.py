import time
from fastapi import FastAPI, Depends, UploadFile, File, Request
from backend.observability.telemetry import TelemetryMiddleware
from backend.core.middleware import MemoryGuardMiddleware
from backend.core.health import router as health_router
from backend.core.orchestrator import hyper_engine
from backend.core.security import setup_cors, verify_token
from backend.routers.paypal import router as paypal_router
from backend.core.ingest import file_processor
from backend.core.logging import setup_logging, logger as struct_logger
from backend.core.database import init_db
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
import os
import psutil
from pydantic import BaseModel
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Initialize Observability Stack
setup_logging()
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)

# Initialize Rate Limiter
limiter = Limiter(key_func=get_remote_address)

class QueryRequest(BaseModel):
    query: str

app = FastAPI(title="Project HYPER SaaS")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.on_event("startup")
async def startup_event():
    """Perform production startup routine."""
    init_db()
    struct_logger.info("system_startup", status="ready", env=os.getenv("APP_ENV", "development"))

# Instrument FastAPI for Tracing
FastAPIInstrumentor.instrument_app(app)

# Add Observability and Resilience Middleware
app.add_middleware(TelemetryMiddleware)
app.add_middleware(MemoryGuardMiddleware)

# Setup CORS (Must be outermost to handle preflights correctly)
setup_cors(app)

# --- Standard Monitoring Endpoints ---
@app.get("/health", tags=["health"])
@limiter.limit("5/minute")
async def health(request: Request):
    """Liveness probe for Docker/CI/CD."""
    return {"status": "ok", "timestamp": time.time()}

@app.get("/api/v1/compute/telemetry", tags=["monitoring"])
@limiter.limit("10/minute")
async def telemetry(request: Request, token: dict = Depends(verify_token)):
    """System resource telemetry for the frontend dashboard."""
    return {
        "cpu": {
            "average_utilization": psutil.cpu_percent(),
            "count": psutil.cpu_count()
        },
        "memory": {
            "percent_used": psutil.virtual_memory().percent,
            "total_gb": round(psutil.virtual_memory().total / (1024**3), 2),
            "used_gb": round(psutil.virtual_memory().used / (1024**3), 2)
        },
        "status": "nominal"
    }

from backend.core.tasks import process_ai_query_task, ingest_document_task, celery_app
from celery.result import AsyncResult

# --- Job Status API ---
@app.get("/api/v1/jobs/{job_id}", tags=["jobs"])
@limiter.limit("20/minute")
async def get_job_status(request: Request, job_id: str, token: dict = Depends(verify_token)):
    """Check the status of a background AI job."""
    result = AsyncResult(job_id, app=celery_app)
    return {
        "job_id": job_id,
        "status": result.status,
        "result": result.result if result.ready() else None
    }

# --- Business Routes ---

@app.post("/api/v1/orchestrate", tags=["ai"])
@limiter.limit("5/minute")
async def orchestrate(request: Request, query_req: QueryRequest, token: dict = Depends(verify_token)):
    user_id = token.get("uid")
    tenant_id = token.get("tenant_id", "default")
    request_id = f"REQ_{user_id}_{int(time.time())}"
    
    # Offload to Celery with Tenant Isolation
    task = process_ai_query_task.delay(query_req.query, request_id, tenant_id=tenant_id)
    
    return {
        "status": "queued",
        "job_id": task.id,
        "request_id": request_id,
        "tenant_id": tenant_id
    }

@app.post("/api/v1/ingest/upload", tags=["ingest"])
@limiter.limit("3/minute")
async def upload_file(request: Request, file: UploadFile = File(...), token: dict = Depends(verify_token)):
    user_id = token.get("uid")
    tenant_id = token.get("tenant_id", "default")
    text = await file_processor.extract_text(file)
    
    if len(text) > 5:
        # Offload ingestion to background with tenant metadata
        task = ingest_document_task.delay(text, file.filename, user_id, tenant_id=tenant_id)
        return {
            "filename": file.filename,
            "status": "processing",
            "job_id": task.id,
            "tenant_id": tenant_id
        }
    
    return {"filename": file.filename, "status": "skipped", "reason": "too_short"}

# Include core routes with prefixes
app.include_router(health_router, prefix="/api/v1/health")
app.include_router(paypal_router, prefix="/api/v1/billing", tags=["billing"])

@app.get("/")
async def root():
    return {"message": "Project HYPER SaaS Engine Active", "docs": "/docs"}
