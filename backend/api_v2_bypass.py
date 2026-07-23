from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import sys
import os

# Add root to sys.path to allow imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.paradigm_bypass.orchestrator import LEO_100_Percent_Engine

router = APIRouter(prefix="/v2/bypass", tags=["7-Layer Irrelevance Architecture"])
engine = LEO_100_Percent_Engine()

class InferenceRequest(BaseModel):
    query: str
    backend_preference: str = None

@router.post("/infer")
async def infer(req: InferenceRequest):
    try:
        task = {"query": req.query, "backend_preference": req.backend_preference, "type": "generic"}
        # Some basic type inference
        if "binary" in req.query.lower(): task["type"] = "binary_logical"
        elif "matrix" in req.query.lower(): task["type"] = "dense_matrix"
        
        result = engine.process(task)
        return {"status": "success", "response": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def status():
    return engine.benchmark_100_percent()

@router.get("/topology")
async def topology():
    return engine.layer4_parallel.topology

@router.post("/cache/clear")
async def clear_cache():
    engine.layer6_quality.cache.cache.clear()
    return {"status": "cleared"}
