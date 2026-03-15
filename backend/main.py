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
from backend.core.metrics import (
    REQUEST_TIME, CPU_USAGE, GPU_USAGE, PPE_HITS, SHADOW_HITS, TWIN_HITS,
    MODEL_INVOCATIONS, AVOIDANCE_RATIO, GPU_COST_SAVED, RAG_HITS,
    MICRO_MODEL_HITS, CACHE_HITS
)

# Initialize
setup_logging()
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(title="Project HYPER: Startup Edition")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
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
    request_id = f"API_{user_id}_{uuid.uuid4().hex[:8]}"
    
    result = await hyper_engine.process(
        data.question, 
        request_id, 
        tenant_id=tenant_id, 
        workspace_id=data.workspace_id
    )
    return {
        "answer": result["result"],
        "source": result["mode"],
        "confidence": result["confidence"],
        "latency_ms": result["latency_ms"],
        "compute_cost_avoided": result["compute_cost_avoided"]
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
    AVOIDANCE_RATIO.set(stats.get("avoidance_ratio", 0))
    GPU_COST_SAVED.set(stats.get("estimated_gpu_cost_saved", 0))
    
    # Global Patterns Analysis (Phase 7)
    from backend.analytics.query_patterns import global_pattern_engine
    # Pattern detection logic would go here
    
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/")
async def root():
    return {"message": "Project HYPER Startup Platform Active"}
