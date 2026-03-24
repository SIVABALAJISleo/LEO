import time
import asyncio
import uuid
import psutil
import os
from typing import Optional
from fastapi import FastAPI, Depends, UploadFile, File, Request, Response
from pydantic import BaseModel
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST, Summary, Gauge, Counter as PromCounter
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from backend.core.database import init_db
from backend.core.orchestrator import hyper_engine
from backend.core.security import setup_cors, verify_token
from backend.core.logging import setup_logging, logger as struct_logger
from backend.core.request_queue import global_request_queue
from backend.core.middleware import MemoryGuardMiddleware
from backend.core.metrics import (
    MODEL_INVOCATIONS, AVOIDANCE_RATIO, GPU_COST_SAVED, RAG_HITS,
    MICRO_MODEL_HITS, CACHE_HITS, COST_SAVED_TOTAL, ENHANCEMENT_HITS,
    CPU_USAGE
)

# Initialize
setup_logging()
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(title="Project HYPER: Startup Edition")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(MemoryGuardMiddleware, max_mem_percent=90.0)
setup_cors(app)

@app.on_event("startup")
async def startup_event():
    init_db()
    await hyper_engine.start()
    asyncio.create_task(global_request_queue.start())
    struct_logger.info("startup", status="ready")

# --- Startup API Portfolio (Phase 7 & 10) ---

class StartupQuery(BaseModel):
    question: str
    workspace_id: str = "default"

@app.post("/api/v1/query", tags=["product"])
@limiter.limit("20/minute")
async def api_query(request: Request, data: StartupQuery, token: dict = Depends(verify_token)):
    user_id = token.get("uid")
    tenant_id = token.get("tenant_id", "default")
    
    from backend.core.usage_metering import global_usage_meter
    if not global_usage_meter.check_limit(user_id, "free"): # Default to free for legacy
        from fastapi import HTTPException
        raise HTTPException(status_code=429, detail="API Limit Exceeded. Upgrade to SaaS Pro.")
        
    start_time = time.time()
    request_id = f"API_{user_id}_{uuid.uuid4().hex[:8]}"
    
    result = await hyper_engine.process(
        data.question, 
        request_id, 
        tenant_id=tenant_id, 
        workspace_id=data.workspace_id
    )
    
    global_usage_meter.record_usage(user_id)
    
    return {
        "answer": result.get("answer") or result.get("result"),
        "source": result.get("source") or result.get("mode"),
        "confidence": result.get("confidence", 0.0),
        "latency_ms": int((time.time() - start_time) * 1000),
        "cost_saved": result.get("cost_saved", 0.0)
    }

# --- SaaS Optimization API (Phase 8) ---

class OptimizeRequest(BaseModel):
    query: str
    tier: str = "free"

@app.post("/api/v1/optimize", tags=["product"])
async def api_optimize(request: Request, data: OptimizeRequest, token: dict = Depends(verify_token)):
    user_id = token.get("uid")
    tenant_id = token.get("tenant_id", "default")
    
    from backend.core.usage_metering import global_usage_meter
    if not global_usage_meter.check_limit(user_id, data.tier):
        from fastapi import HTTPException
        raise HTTPException(status_code=429, detail="SaaS Tier Limit Exceeded")
    
    start_time = time.time()
    request_id = f"OPT_{user_id}_{uuid.uuid4().hex[:8]}"
    
    result = await hyper_engine.process(
        data.query, 
        request_id, 
        tenant_id=tenant_id
    )
    
    global_usage_meter.record_usage(user_id)
    
    return {
        "answer": result.get("answer") or result.get("result"),
        "confidence": result.get("confidence", 0.0),
        "latency_ms": int((time.time() - start_time) * 1000),
        "source": result.get("source", "MODEL_LADDER"),
        "model_used": "hyper_optimization" if result.get("cost_saved") else "large_model_fallback",
        "cost_saved": result.get("cost_saved", 0.0)
    }


@app.get("/api/v1/analytics/{workspace_id}", tags=["product"])
async def get_analytics(workspace_id: str, token: dict = Depends(verify_token)):
    from backend.analytics.cost_monitor import global_cost_monitor
    return global_cost_monitor.calculate_savings(workspace_id)

@app.get("/api/v1/workspaces", tags=["product"])
async def list_workspaces(token: dict = Depends(verify_token)):
    return [{"id": "default", "name": "Default Workspace"}]

@app.post("/api/v1/documents", tags=["product"])
async def upload_document(file: UploadFile = File(...), workspace_id: str = "default", token: dict = Depends(verify_token)):
    from backend.ingest.document_indexer import global_document_indexer
    # In a real environment, we'd save the file first
    return {"status": "success", "message": f"Document {file.filename} is being indexed."}

@app.get("/health")
async def health():
    return {"status": "ok", "timestamp": time.time()}

@app.get("/metrics")
async def metrics():
    CPU_USAGE.set(psutil.cpu_percent())
    from backend.analytics.cost_monitor import global_cost_monitor
    stats = global_cost_monitor.calculate_savings("default")
    
    # Phase 5: Update Prometheus gauges with real avoidance data
    telemetry = hyper_engine.get_telemetry()
    AVOIDANCE_RATIO.set(telemetry.get("inference_avoidance_ratio", 0))
    GPU_COST_SAVED.set(stats.get("estimated_gpu_cost_saved", 0))
    
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/api/v1/telemetry", tags=["observability"])
async def get_telemetry():
    """Phase 5: Real-time inference avoidance telemetry."""
    return hyper_engine.get_telemetry()

@app.get("/")
async def root():
    return {"message": "Project HYPER Startup Platform Active"}
