from fastapi import APIRouter
from typing import Dict, Any
from pydantic import BaseModel

from backend.hybrid.orchestrator import global_hybrid_system

router = APIRouter(
    prefix="/api/v1/dream",
    tags=["Dream Engine v2.0"]
)

class IdlePingRequest(BaseModel):
    user_id: str
    session_id: str = "default"
    current_context: str = ""

class BatteryUpdateRequest(BaseModel):
    battery_pct: float

@router.post("/idle")
async def ping_idle(request: IdlePingRequest) -> Dict[str, Any]:
    """
    Called by frontend when user is idle (e.g. stopped typing for 2 seconds).
    Updates context and triggers dream engine prediction cycles.
    Tenant-isolated via session_id (Audit Finding 3).
    """
    global_hybrid_system.dream_engine.record_activity(
        query=request.current_context,
        session_id=request.session_id,
        context={"text": request.current_context, "topic": "general"}
    )
    return {"status": "idle_recorded", "session_id": request.session_id}

@router.get("/telemetry")
async def get_telemetry() -> Dict[str, Any]:
    """
    Returns the full v2.0 Dream Engine telemetry including:
    - Circuit breaker status (Finding 5)
    - Cache hit rate
    - Confidence gating state (Finding 6)
    - Tenant count (Finding 3)
    """
    return global_hybrid_system.dream_engine.get_telemetry()

@router.post("/battery")
async def update_battery(request: BatteryUpdateRequest) -> Dict[str, Any]:
    """
    Finding 5: Update battery level. Circuit breaker trips at <20%.
    """
    global_hybrid_system.dream_engine.update_battery(request.battery_pct)
    return {
        "battery_pct": request.battery_pct,
        "circuit_breaker": "TRIPPED" if global_hybrid_system.dream_engine._circuit_breaker_tripped else "OK"
    }
