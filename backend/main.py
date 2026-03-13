import time
from fastapi import FastAPI, Depends, UploadFile, File
from backend.observability.telemetry import TelemetryMiddleware
from backend.core.health import router as health_router
from backend.core.orchestrator import hyper_engine
from backend.core.security import setup_cors, verify_firebase_token
from backend.routers.paypal import router as paypal_router
from backend.core.ingest import file_processor
from pydantic import BaseModel
import psutil

app = FastAPI(title="Project HYPER SaaS")

# Add Observability Middleware
app.add_middleware(TelemetryMiddleware)

# Setup CORS (Must be outermost to handle preflights correctly)
setup_cors(app)

# --- Standard Monitoring Endpoints ---
@app.get("/health", tags=["health"])
async def health():
    """Liveness probe for Docker/CI/CD."""
    return {"status": "ok", "timestamp": time.time()}

@app.get("/api/v1/compute/telemetry", tags=["monitoring"])
async def telemetry(token: dict = Depends(verify_token)):
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

# --- Shared Schemas ---
class QueryRequest(BaseModel):
    query: str

# --- Business Routes (Prefixed via Routers if possible, or direct) ---

@app.post("/api/v1/orchestrate", tags=["ai"])
async def orchestrate(request: QueryRequest, token: dict = Depends(verify_token)):
    user_id = token.get("uid")
    return await hyper_engine.process(request.query, f"REQ_{user_id}_{int(time.time())}")

@app.post("/api/v1/ingest/upload", tags=["ingest"])
async def upload_file(file: UploadFile = File(...), token: dict = Depends(verify_token)):
    user_id = token.get("uid")
    text = await file_processor.extract_text(file)
    
    # Automatically index in RAG
    if len(text) > 5:
        await hyper_engine.rag.add_documents([text])
        
    return {
        "filename": file.filename,
        "content_length": len(text),
        "status": "ingested",
        "user_id": user_id
    }

# Include core routes with prefixes
app.include_router(health_router, prefix="/api/v1/health")
app.include_router(paypal_router, prefix="/api/v1/billing", tags=["billing"])

@app.get("/")
async def root():
    return {"message": "Project HYPER SaaS Engine Active", "docs": "/docs"}
