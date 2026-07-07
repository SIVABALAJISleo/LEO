import logging
from fastapi import APIRouter, Request, Depends
from pydantic import BaseModel, Field
from typing import Optional

from backend.layers.v42_ultimate_orchestrator import global_v42_ultimate_orchestrator
from backend.layers.v43_software_first_orchestrator import get_v43_orchestrator
from backend.layers.v_infinity_orchestrator import get_vinfinity_orchestrator

from backend.security.rbac import PermissionChecker

router = APIRouter()
logger = logging.getLogger(__name__)

# Lazy singletons
_v43 = None
_vinfinity = None

def _get_v43():
    global _v43
    if _v43 is None:
        _v43 = get_v43_orchestrator()
    return _v43

def _get_vinfinity():
    global _vinfinity
    if _vinfinity is None:
        _vinfinity = get_vinfinity_orchestrator()
    return _vinfinity

class OrchestrateRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=8000, description="The user's semantic query.")
    workspace_id: str = Field("default", description="Tenant / workspace identifier.")
    quality_hint: Optional[str] = Field(None, description="Optional quality hint: ultra|balanced|lightweight|emergency")

async def _do_orchestrate(body: OrchestrateRequest):
    logger.info(f"[VInfinity] Orchestrating: workspace={body.workspace_id} query_len={len(body.query)}")
    result = _get_vinfinity().execute_semantic_workflow(
        query=body.query,
        context={"workspace_id": body.workspace_id, "quality_hint": body.quality_hint},
    )
    return result

@router.post("/api/v1/leo/orchestrate", tags=["LEO Orchestration"])
async def leo_orchestrate(request: Request, body: OrchestrateRequest, token: dict = Depends(PermissionChecker("orchestrate"))):
    return await _do_orchestrate(body)

@router.post("/api/v1/leo/vinfinity/orchestrate", tags=["LEO v∞ Orchestration"])
async def leo_vinfinity_orchestrate(request: Request, body: OrchestrateRequest, token: dict = Depends(PermissionChecker("orchestrate"))):
    return await _do_orchestrate(body)

@router.post("/api/v1/leo/v43/orchestrate", tags=["LEO V43 Orchestration"])
async def leo_v43_orchestrate(request: Request, body: OrchestrateRequest, token: dict = Depends(PermissionChecker("orchestrate"))):
    logger.info(f"[V43-COMPAT] Orchestrating: workspace={body.workspace_id}")
    result = _get_v43().execute_semantic_workflow(
        query=body.query,
        context={"workspace_id": body.workspace_id, "quality_hint": body.quality_hint},
    )
    return result

@router.post("/api/v1/leo/v42/orchestrate", tags=["LEO V42 Orchestration (legacy)"])
async def leo_v42_orchestrate(request: Request, body: OrchestrateRequest, token: dict = Depends(PermissionChecker("orchestrate"))):
    logger.info(f"[V42-COMPAT] Orchestrating: workspace={body.workspace_id}")
    result = global_v42_ultimate_orchestrator.execute_semantic_workflow(
        query=body.query,
        context={"workspace_id": body.workspace_id, "quality_hint": body.quality_hint},
    )
    return result

@router.post("/api/v1/leo/query", tags=["LEO Orchestration"])
async def leo_query_alias(request: Request, body: OrchestrateRequest, token: dict = Depends(PermissionChecker("orchestrate"))):
    return await _do_orchestrate(body)

@router.post("/api/v1/query", tags=["LEO Orchestration"])
async def legacy_query(request: Request, body: OrchestrateRequest, token: dict = Depends(PermissionChecker("orchestrate"))):
    return await _do_orchestrate(body)
