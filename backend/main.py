import time
from fastapi import FastAPI, Depends, UploadFile, File, Request
from backend.observability.telemetry import TelemetryMiddleware
from backend.core.middleware import MemoryGuardMiddleware
from backend.core.metering import UsageMeteringMiddleware
from backend.core.health import router as health_router
from backend.core.orchestrator import hyper_engine
from backend.core.security import setup_cors, verify_token
from backend.routers.paypal import router as paypal_router
from backend.core.ingest import file_processor
from backend.core.logging import setup_logging, logger as struct_logger
from backend.core.database import init_db
from backend.core.request_queue import global_request_queue
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from prometheus_fastapi_instrumentator import Instrumentator
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
    stream: bool = False

app = FastAPI(title="Project HYPER SaaS")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.on_event("startup")
async def startup_event():
    """Perform production startup routine."""
    init_db()
    # Start the intelligent request queue
    asyncio.create_task(global_request_queue.start())
    struct_logger.info("system_startup", status="ready", env=os.getenv("APP_ENV", "development"))

# Instrument FastAPI for Tracing
FastAPIInstrumentor.instrument_app(app)

# Expose Prometheus Metrics
Instrumentator().instrument(app).expose(app)

# Add Observability and Resilience Middleware
app.add_middleware(TelemetryMiddleware)
app.add_middleware(MemoryGuardMiddleware)
app.add_middleware(UsageMeteringMiddleware)

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

# from backend.core.tasks import process_ai_query_task, ingest_document_task, celery_app
from celery.result import AsyncResult

# --- Job Status API ---
@app.get("/api/v1/jobs/{job_id}", tags=["jobs"])
@limiter.limit("20/minute")
async def get_job_status(request: Request, job_id: str, token: dict = Depends(verify_token)):
    """Check the status of a background AI job."""
    from backend.core.tasks import celery_app
    result = AsyncResult(job_id, app=celery_app)
    return {
        "job_id": job_id,
        "status": result.status,
        "result": result.result if result.ready() else None
    }

# --- Business Routes ---

@app.post("/api/v1/orchestrate", tags=["ai"])
@limiter.limit("10/minute")
async def orchestrate(request: Request, query_req: QueryRequest, token: dict = Depends(verify_token)):
    user_id = token.get("uid")
    tenant_id = token.get("tenant_id", "default")
    tier = token.get("tier", "free")
    request_id = f"REQ_{user_id}_{int(time.time())}"
    
    # SaaS Enforcement: Check Daily Limits
    from backend.core.database import SessionLocal
    from backend.core.metering import check_subscription_limits
    db = SessionLocal()
    try:
        if not check_subscription_limits(db, tenant_id, user_id, tier):
            from fastapi import HTTPException
            raise HTTPException(status_code=403, detail="SaaS Subscription Limit Exceeded. Please upgrade.")
        
        # 1. STREAMING FLOW
        if query_req.stream:
            from fastapi.responses import StreamingResponse
            async def stream_wrapper():
                async for chunk in hyper_engine.process_stream(query_req.query, request_id, tenant_id=tenant_id):
                    yield chunk
            return StreamingResponse(stream_wrapper(), media_type="text/event-stream")

        # 2. LOAD-CONTROLLED SYNCHRONOUS FLOW
        async def run_task():
            # Adaptive Timeout: Higher tiers get more time
            timeout = 30 if tier == "enterprise" else 15
            try:
                return await asyncio.wait_for(
                    hyper_engine.process(query_req.query, request_id, tenant_id=tenant_id),
                    timeout=timeout
                )
            except asyncio.TimeoutError:
                return {"error": "Request timed out. Try a smaller query or upgrade tier."}

        result = await global_request_queue.add(run_task, request_id)
        return {
            "status": "success",
            "request_id": request_id,
            "tenant_id": tenant_id,
            "tier": tier,
            "result": result
        }
    finally:
        db.close()

@app.post("/api/v1/ingest/upload", tags=["ingest"])
@limiter.limit("3/minute")
async def upload_file(request: Request, file: UploadFile = File(...), token: dict = Depends(verify_token)):
    user_id = token.get("uid")
    tenant_id = token.get("tenant_id", "default")
    text = await file_processor.extract_text(file)
    
    if len(text) > 5:
        from backend.core.tasks import ingest_document_task
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
