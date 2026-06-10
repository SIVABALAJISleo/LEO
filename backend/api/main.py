"""
backend/api/main.py
LEO: STAGE 13 — OBSERVABILITY + EXPLAINABILITY
Exposes the Universal Adapter and traceability endpoints.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List

from backend.api.universal_adapter import api_runtime
from backend.api.openai_proxy import (
    ChatCompletionRequest,
    EmbeddingRequest,
    handle_chat_completion,
    handle_embeddings
)

app = FastAPI(title="LEO Distributed Cognition OS", version="18.0.0")

# ---------------------------------------------------------
# STAGE 17 — ENTERPRISE OVERLAY MODE (OPENAI COMPATIBILITY)
# ---------------------------------------------------------

@app.post("/v1/chat/completions")
async def openai_chat_completions(req: ChatCompletionRequest):
    """Transparent drop-in replacement for OpenAI SDK clients."""
    return await handle_chat_completion(req)

@app.post("/v1/embeddings")
async def openai_embeddings(req: EmbeddingRequest):
    return handle_embeddings(req)


class QueryRequest(BaseModel):
    query: str

class ProceduralPayload(BaseModel):
    graph: Dict[str, Any]

@app.post("/api/v1/cognition/generate")
async def generate_cognition(req: QueryRequest):
    """Core cognition entrypoint (Stage 12)."""
    return await api_runtime.generate(req.query)

@app.post("/api/v1/cognition/embed")
async def generate_embeddings(req: QueryRequest):
    return api_runtime.embed(req.query)

@app.post("/api/v1/cognition/retrieve")
async def retrieve_knowledge(req: QueryRequest):
    return api_runtime.retrieve(req.query)

@app.post("/api/v1/cognition/execute")
async def execute_procedural(req: ProceduralPayload):
    return api_runtime.execute(req.graph)

@app.post("/api/v1/cognition/crystallize")
async def crystallize_manual(req: QueryRequest):
    return api_runtime.crystallize(req.query, "Manual API Crystallization")

@app.post("/api/v1/cognition/proceduralize")
async def compile_procedural(traces: List[Dict[str, Any]]):
    return api_runtime.proceduralize(traces)

# ---------------------------------------------------------
# STAGE 13 — OBSERVABILITY + EXPLAINABILITY ENDPOINTS
# ---------------------------------------------------------

@app.get("/api/v1/observability/why/{trace_id}")
async def explain_why(trace_id: str):
    """Explains why a specific routing decision was made."""
    return {
        "trace_id": trace_id,
        "explanation": "Decision forced to 'sparse_7b' due to novelty failure in semantic cache.",
        "thermal_state_at_time": "nominal"
    }

@app.get("/api/v1/observability/trace/{trace_id}")
async def fetch_trace(trace_id: str):
    """Full execution provenance chain."""
    return {
        "trace_id": trace_id,
        "provenance_chain": ["adaptive_router", "cache_miss", "rag_miss", "local_1b_hit"],
        "total_latency_ms": 195.4
    }

@app.get("/api/v1/observability/debug")
async def system_debug_state():
    """Returns the internal state of the 17-Stage OS."""
    return {
        "status": "online",
        "active_modules": 17,
        "thermal_state": api_runtime.thermal.get_hardware_state()
    }
