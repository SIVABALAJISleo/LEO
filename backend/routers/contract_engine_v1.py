"""
backend/routers/contract_engine_v1.py
FastAPI Router for LEO Contract Engine v1.0
5-Tier Bounded Escape Ladder & Calibrated Verifier Gate
"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Any, List
from leo.contract_engine_v1 import get_contract_engine_v1

router = APIRouter(prefix="/api/v1/contract-v1", tags=["Contract Engine v1.0"])

class QueryRequest(BaseModel):
    query: str

@router.post("/execute")
async def execute_query(req: QueryRequest):
    """
    Executes a query through the 5-Tier Bounded Escape Ladder:
    Tier 0 (Exact Cache) -> Tier 1 (Semantic Subsumption) -> Tier 2 (Distilled Student iGPU) -> Verifier Gate
    """
    engine = get_contract_engine_v1()
    return engine.execute(req.query)

@router.get("/spec")
async def get_contract_spec():
    """Returns the active formal contract specification"""
    engine = get_contract_engine_v1()
    return {
        "task": engine.contract.task,
        "tau_threshold": engine.contract.tau_threshold,
        "max_latency_p95_ms": engine.contract.max_latency_p95_ms,
        "required_checks": engine.contract.required_checks,
        "hardware_target": "Intel Core i5-12450H (8c/12t) + Intel UHD Graphics (48 EUs)"
    }

@router.get("/telemetry")
async def get_telemetry():
    """Returns global escape rate, tier distribution, and audit log"""
    engine = get_contract_engine_v1()
    return {
        "total_queries": engine.total_queries,
        "tier_distribution": engine.tier_hits,
        "escapes_count": engine.escapes_count,
        "recent_logs": engine.telemetry_log[-10:] if engine.telemetry_log else []
    }
