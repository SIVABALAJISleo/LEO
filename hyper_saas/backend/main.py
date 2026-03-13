import time
from fastapi import FastAPI, Depends, UploadFile, File
from hyper_saas.backend.observability.telemetry import TelemetryMiddleware
from hyper_saas.backend.core.health import router as health_router
from hyper_saas.backend.core.orchestrator import hyper_engine
from hyper_saas.backend.core.security import setup_cors, verify_firebase_token
from hyper_saas.backend.core.billing import router as billing_router
from hyper_saas.backend.core.ingest import file_processor
from pydantic import BaseModel

app = FastAPI(title="Project HYPER SaaS")

# Setup CORS
# Add Observability Middleware
app.add_middleware(TelemetryMiddleware)

# Setup CORS (Must be outermost to handle preflights correctly)
setup_cors(app)

class QueryRequest(BaseModel):
    query: str

@app.post("/api/v1/orchestrate")
async def orchestrate(request: QueryRequest, token: dict = Depends(verify_firebase_token)):
    user_id = token.get("uid")
    return await hyper_engine.process(request.query, f"REQ_{user_id}_{int(time.time())}")

@app.post("/api/v1/ingest/upload")
async def upload_file(file: UploadFile = File(...), token: dict = Depends(verify_firebase_token)):
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

# Include core routes
app.include_router(health_router)
app.include_router(billing_router)

@app.get("/")
async def root():
    return {"message": "Project HYPER SaaS Engine Active"}
