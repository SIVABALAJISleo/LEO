"""
FastAPI Router for Intelligence Resonance Architecture (IRA)
Provides the API endpoints to interact with the full 8-Pillar System.
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

from core.ira import TriComputeOrchestrator, IRAConfig
from core.ira.shared.logging import IRALogger

router = APIRouter(prefix="/ira", tags=["Intelligence Resonance Architecture"])

# Singleton Instance (initialized on startup in main app, or lazy loaded here)
_tco_instance: Optional[TriComputeOrchestrator] = None

class IRAQueryRequest(BaseModel):
    query: str = Field(..., description="The user's query")
    max_tokens: int = Field(256, description="Max tokens for neural generation")
    temperature: float = Field(0.7, description="Temperature for neural generation")
    
class IRAQueryResponse(BaseModel):
    response: str
    total_latency_ms: float
    pillar_used: str
    cache_hit: bool
    symbolic_handled: bool
    precomputed: bool
    layers_used: int
    effective_tok_s: float
    adr_complexity: str
    pse_acceptance_rate: float
    error: Optional[str] = None
    compute_breakdown: Dict[str, Any]

def get_tco() -> TriComputeOrchestrator:
    global _tco_instance
    if _tco_instance is None:
        _tco_instance = TriComputeOrchestrator(IRAConfig.from_env())
    return _tco_instance

@router.post("/query", response_model=IRAQueryResponse)
async def query_ira(request: IRAQueryRequest, background_tasks: BackgroundTasks):
    """
    Main endpoint for sending queries to the Intelligence Resonance Architecture.
    """
    tco = get_tco()
    try:
        # The TCO handles the entire synchronous/asynchronous pipeline internally
        # We wrap it here to allow FastAPI to handle requests concurrently
        # If we expect it to block, we could run it in a threadpool, but for now we call it directly.
        
        result = tco.process(
            query=request.query,
            max_tokens=request.max_tokens,
            temperature=request.temperature
        )
        
        return IRAQueryResponse(
            response=result.text,
            total_latency_ms=result.total_latency_ms,
            pillar_used=result.pillar_used,
            cache_hit=result.cache_hit,
            symbolic_handled=result.symbolic_handled,
            precomputed=result.precomputed,
            layers_used=result.layers_used,
            effective_tok_s=result.effective_tok_s,
            adr_complexity=result.adr_complexity,
            pse_acceptance_rate=result.pse_acceptance_rate,
            error=result.error,
            compute_breakdown=result.compute_breakdown
        )
        
    except Exception as e:
        IRALogger.get_logger("api").error(f"Error in /ira/query: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/load_models")
async def load_models():
    """
    Pre-load the local LLMs (Draft and Main) into memory.
    """
    tco = get_tco()
    try:
        tco.load_models()
        return {"status": "models loaded successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def get_status():
    """
    Get metrics, sparsity reports, QSM hits, and general system health.
    """
    tco = get_tco()
    return tco.get_system_report()

@router.post("/shutdown")
async def shutdown_system(background_tasks: BackgroundTasks):
    """
    Gracefully shut down the system and persist data.
    """
    tco = get_tco()
    background_tasks.add_task(tco.shutdown)
    return {"status": "shutdown initiated"}
