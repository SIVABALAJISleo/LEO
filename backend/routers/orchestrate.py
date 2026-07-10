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

# --- On-device Training Endpoint (Layer 7) ---
class TrainRequest(BaseModel):
    pairs: list[tuple[str, str]] = Field(..., description="Prompt-response pairs to train on")
    output_dir: str = Field("models/adapters/local_node", description="Output directory for adapters")
    epochs: int = Field(8, description="Number of training epochs")
    lr: float = Field(5e-4, description="Learning rate")

@router.post("/api/v1/train", tags=["LEO Training"], summary="Fine-tune LoRA adapters on CPU/iGPU")
async def run_on_device_training(body: TrainRequest, token: dict = Depends(PermissionChecker("orchestrate"))):
    from backend.training.lora_trainer import LoRATrainer
    trainer = LoRATrainer()
    metrics = trainer.train(body.pairs, output_dir=body.output_dir, epochs=body.epochs, lr=body.lr)
    return metrics

# --- LEO v∞ Telemetry & Self-Evolution Endpoints (Layer 15 & 18) ---
@router.post("/api/v1/leo/vinfinity/benchmark", tags=["LEO v∞ Telemetry"])
async def run_vinfinity_benchmark(token: dict = Depends(PermissionChecker("orchestrate"))):
    from backend.benchmarks.infinity_bench import run_benchmark
    report = run_benchmark()
    return report

@router.post("/api/v1/leo/vinfinity/evolve", tags=["LEO v∞ Telemetry"])
async def trigger_vinfinity_evolution(token: dict = Depends(PermissionChecker("orchestrate"))):
    from backend.learning.self_improvement import get_evolution_loop
    evo_result = get_evolution_loop().run_evolution_cycle()
    return evo_result

@router.get("/api/v1/leo/vinfinity/evolution/history", tags=["LEO v∞ Telemetry"])
async def get_evolution_history(token: dict = Depends(PermissionChecker("orchestrate"))):
    from backend.learning.self_improvement import get_evolution_loop
    return {
        "total_generations": get_evolution_loop().generation,
        "best_fitness": get_evolution_loop()._best_fitness,
        "history": get_evolution_loop().get_history()
    }

class TelemetryEntry(BaseModel):
    prompt_class: str = Field(..., description="The class of the prompt (e.g. cacheable, novel)")
    latency_ms: float = Field(..., description="End-to-end latency in ms")
    was_avoided: bool = Field(False, description="Whether compute was avoided via cache/surrogate")
    hardware_hash: Optional[str] = Field(None, description="Anonymized hardware identifier")

@router.post("/api/v1/leo/vinfinity/telemetry", tags=["LEO v∞ Telemetry"])
async def submit_telemetry(entry: TelemetryEntry, token: dict = Depends(PermissionChecker("orchestrate"))):
    from backend.analytics.telemetry_collector import get_telemetry_collector
    collector = get_telemetry_collector()
    collector.record_inference(
        prompt_class=entry.prompt_class,
        latency_ms=entry.latency_ms,
        was_avoided=entry.was_avoided,
        hardware_hash=entry.hardware_hash,
    )
    return {"status": "recorded"}

# --- LEO V44 "OMNISCIENCE" Cryptographic Proof of Intelligence Endpoints ---
@router.get("/api/v1/leo/v44/poi/ledger", tags=["LEO V44 Omniscience"])
async def get_poi_ledger_endpoint(token: dict = Depends(PermissionChecker("orchestrate"))):
    from backend.security.poi_ledger import get_poi_ledger
    ledger = get_poi_ledger()
    return {
        "verified": ledger.verify_chain(),
        "blocks": [b.to_dict() for b in ledger.chain]
    }

@router.get("/api/v1/leo/v44/poi/verify", tags=["LEO V44 Omniscience"])
async def verify_seal_endpoint(signature: str, token: dict = Depends(PermissionChecker("orchestrate"))):
    from backend.security.poi_ledger import get_poi_ledger
    ledger = get_poi_ledger()
    for block in ledger.chain:
        if block.seal_signature == signature:
            return {
                "authentic": True,
                "block_index": block.index,
                "timestamp": block.timestamp,
                "metrics": block.metrics
            }
    return {"authentic": False}


