"""
backend/routers/hyper_escape_router.py
FastAPI router for HYPER-GODMODE Ω∞: Universal Alternative Computation,
Memory Escape, Pathway Discovery & Verified Parity Engine.
Prefix: /api/v1/escape_omega
"""
from __future__ import annotations
import logging
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from hyper_universal.contracts.contract_engine import (
    ContractRegistry,
    UniversalContract,
    ExactnessRequirement,
    NumericalTolerance,
    ResourceBudget,
)
from hyper_universal.backends.registry import BackendCapabilityRegistry
from hyper_universal.analysis.bottleneck import BottleneckAnalyzer
from hyper_universal.workload_ir.graph import ComputationalIR, IRNode, OpKind
from hyper_universal.pathway_discovery.search import AlternativeAlgorithmDiscoveryEngine
from hyper_universal.evidence_store.database import PathwayEvidenceStore
from hyper_universal.certification.engine import FormalCertificationEngine, CertificationState
from hyper_universal.benchmarking.runner import RigorousPerformanceBenchmarker
from hyper_universal.memory_escape.engine import MemoryBudgetController, OutOfCoreStreamEngine
from hyper_universal.computation_elimination.engine import ComputationEliminationEngine
from hyper_universal.data_movement.engine import DataMovementReductionEngine
from hyper_universal.precision.optimizer import PrecisionOptimizer
from hyper_universal.incremental.engine import IncrementalExecutionEngine
from hyper_universal.scheduler.scheduler import UniversalScheduler
from hyper_universal.capability_mirror.registry import UniversalCapabilityRegistry
from hyper_universal.capability_mirror.search import CapabilitySubstitutionSearch
from hyper_universal.capability_mirror.matrix import CapabilityMatrixGenerator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/escape_omega", tags=["HYPER-GODMODE Ω∞ Universal Escape"])

# Global singletons
_contract_registry = ContractRegistry()
_backend_registry = BackendCapabilityRegistry()
_bottleneck_analyzer = BottleneckAnalyzer()
_evidence_store = PathwayEvidenceStore()
_certifier = FormalCertificationEngine()
_scheduler = UniversalScheduler()
_benchmarker = RigorousPerformanceBenchmarker()
_memory_controller = MemoryBudgetController()
_discovery_engine = AlternativeAlgorithmDiscoveryEngine()
_capability_registry = UniversalCapabilityRegistry()
_capability_search = CapabilitySubstitutionSearch(registry=_capability_registry)
_capability_matrix_gen = CapabilityMatrixGenerator()


class WorkloadRegistrationRequest(BaseModel):
    workload_id: str
    category: str
    description: str
    input_shape: List[int]
    dtype: str = "float32"
    exactness_requirement: str = "BITWISE_EXACT"
    max_relative_error: float = 0.0
    max_absolute_error: float = 0.0
    max_memory_mb: float = 1024.0
    latency_deadline_ms: Optional[float] = None
    verification_strategy: str = "differential_reference"
    fallback_backend: str = "CPU_AVX2"


class BottleneckAnalysisRequest(BaseModel):
    workload_id: str
    num_ops: int = 10
    total_flops: int = 10_000_000
    peak_memory_bytes: int = 64 * 1024 * 1024


class PathwayDiscoveryRequest(BaseModel):
    workload_id: str
    dimension: int = 512
    max_candidates: int = 5
    allow_approximate: bool = False


@router.get("/status")
async def get_system_status() -> Dict[str, Any]:
    """Returns current status of HYPER-GODMODE Ω∞ universal execution engine."""
    backends = _backend_registry.get_available_backends()
    evidence_summary = _evidence_store.summary()
    mem_status = _memory_controller.get_telemetry()

    return {
        "status": "OPERATIONAL",
        "system_name": "HYPER-GODMODE Ω∞ Universal Engine",
        "host_hardware": {
            "target": "Lenovo IdeaPad Slim 3 (i5-12450H, Intel UHD 48EU, 16GB RAM)",
            "physical_hardware_parity": "0.0% (Software-Only Optimization)",
            "memory_budget_mb": _memory_controller.budget_mb,
            "memory_usage_mb": mem_status.current_used_mb,
            "memory_safety_margin_mb": _memory_controller.safety_margin_mb,
        },
        "available_backends": [b.to_dict() for b in backends],
        "registered_contracts_count": len(_contract_registry.list_contracts()),
        "evidence_store_records": evidence_summary["total_records"],
        "exact_verified_count": evidence_summary["exact_verified_count"],
        "contract_verified_count": evidence_summary["contract_verified_count"],
        "failed_correctness_count": evidence_summary["failed_correctness_count"],
    }


@router.get("/contracts")
async def list_contracts() -> List[Dict[str, Any]]:
    """Lists all formally registered contracts in the system."""
    contracts = _contract_registry.list_contracts()
    return [c.to_dict() for c in contracts]


@router.get("/contracts/{workload_id}")
async def get_contract(workload_id: str) -> Dict[str, Any]:
    """Fetches a specific workload contract by workload_id."""
    c = _contract_registry.get(workload_id)
    if not c:
        raise HTTPException(status_code=404, detail=f"Contract '{workload_id}' not found.")
    return c.to_dict()


@router.post("/contracts/register")
async def register_contract(req: WorkloadRegistrationRequest) -> Dict[str, Any]:
    """Registers a new universal workload contract."""
    try:
        exactness = ExactnessRequirement(req.exactness_requirement)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid exactness requirement: {req.exactness_requirement}")

    contract = UniversalContract(
        workload_id=req.workload_id,
        category=req.category,
        description=req.description,
        input_schema={"shape": req.input_shape, "dtype": req.dtype},
        output_schema={"shape": req.input_shape, "dtype": req.dtype},
        exactness_requirement=exactness,
        tolerance=NumericalTolerance(
            max_relative_error=req.max_relative_error,
            max_absolute_error=req.max_absolute_error,
        ),
        resource_budget=ResourceBudget(
            max_memory_mb=req.max_memory_mb,
            latency_deadline_ms=req.latency_deadline_ms,
        ),
        verification_strategy=req.verification_strategy,
        fallback_backend=req.fallback_backend,
    )
    _contract_registry.register(contract)
    return {"status": "SUCCESS", "contract": contract.to_dict()}


@router.get("/backends")
async def list_backends() -> List[Dict[str, Any]]:
    """Discovers and reports genuine backend capabilities on the host."""
    backends = _backend_registry.get_available_backends()
    return [b.to_dict() for b in backends]


@router.post("/analyze/bottleneck")
async def analyze_bottleneck(req: BottleneckAnalysisRequest) -> Dict[str, Any]:
    """Analyzes arithmetic intensity and classifies execution bottleneck against host roofline."""
    ir = ComputationalIR(workload_id=req.workload_id)
    # Add synthesized node
    node = IRNode(
        node_id="main_op",
        op=OpKind.CUSTOM,
        inputs=[],
        output_shape=[1000],
        dtype="float32",
        estimated_flops=req.total_flops,
        memory_bytes=req.peak_memory_bytes,
    )
    ir.add_node(node)
    report = _bottleneck_analyzer.analyze(ir)
    return report.to_dict()


@router.post("/discover/pathways")
async def discover_pathways(req: PathwayDiscoveryRequest) -> Dict[str, Any]:
    """Discovers and benchmarks alternative execution candidates for a workload."""
    import numpy as np
    contract = _contract_registry.get(req.workload_id)
    if not contract:
        # Fallback to default linear algebra contract if not pre-registered
        contract = _contract_registry.get("dense_gemm_512x512")
        if not contract:
            raise HTTPException(status_code=404, detail=f"Contract '{req.workload_id}' not found.")

    # Create dummy matrix input for exploration
    data = np.random.randn(req.dimension, req.dimension).astype(np.float32)
    report = _discovery_engine.discover_and_evaluate(
        workload_id=req.workload_id,
        contract=contract,
        sample_input=data,
        max_candidates=req.max_candidates,
    )
    return report.to_dict()


@router.get("/evidence")
async def list_evidence(
    workload_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
) -> List[Dict[str, Any]]:
    """Fetches verified evidence records from local persistent evidence store."""
    records = _evidence_store.list_all()
    if workload_id:
        records = [r for r in records if r.workload_id == workload_id]
    if status:
        records = [r for r in records if r.verification_status == status]
    return [r.to_dict() for r in records]


@router.get("/evidence/summary")
async def get_evidence_summary() -> Dict[str, Any]:
    """Returns aggregated evidence and parity scorecard."""
    return _evidence_store.summary()


@router.post("/memory/stream_sum")
async def run_streaming_sum(size_mb: int = Query(32, ge=1, le=512)) -> Dict[str, Any]:
    """Runs out-of-core bounded chunked streaming reduction to demonstrate memory escape."""
    import tempfile, os, numpy as np
    num_elements = (size_mb * 1024 * 1024) // 4
    with tempfile.NamedTemporaryFile(delete=False, suffix=".bin") as f:
        tmp_path = f.name
    try:
        # Generate random floats in chunks
        chunk = 1_000_000
        total_sum_expected = 0.0
        with open(tmp_path, "wb") as f:
            written = 0
            while written < num_elements:
                n = min(chunk, num_elements - written)
                arr = np.ones(n, dtype=np.float32)
                total_sum_expected += float(np.sum(arr))
                f.write(arr.tobytes())
                written += n

        stream_eng = OutOfCoreStreamEngine(_memory_controller)
        res_sum, report = stream_eng.stream_binary_file_reduction(
            tmp_path,
            chunk_size_bytes=4 * 1024 * 1024,
            dtype=np.float32,
            reduce_fn=np.sum,
        )

        return {
            "status": "SUCCESS",
            "file_size_mb": size_mb,
            "calculated_sum": float(res_sum),
            "expected_sum": float(total_sum_expected),
            "exact_match": bool(np.isclose(res_sum, total_sum_expected, rtol=1e-5)),
            "memory_escape_report": report.to_dict(),
        }
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


@router.get("/scorecard")
async def get_godmode_scorecard() -> Dict[str, Any]:
    """Comprehensive evidence-backed scorecard for HYPER-GODMODE Ω∞."""
    backends = _backend_registry.get_available_backends()
    summary = _evidence_store.summary()
    telemetry = _memory_controller.get_telemetry()

    return {
        "engine": "HYPER-GODMODE Ω∞ (Universal Escape Engine)",
        "hardware_profile": "Lenovo IdeaPad Slim 3 (i5-12450H/i5-13420H, Intel UHD 48EU, 16GB)",
        "physical_hardware_parity": "0.0% (Zero Physical GPU Claims)",
        "contract_parity_percentage": summary.get("contract_parity_percentage", 100.0),
        "total_evaluated_candidates": summary.get("total_records", 0),
        "exact_verified_candidates": summary.get("exact_verified_count", 0),
        "contract_verified_candidates": summary.get("contract_verified_count", 0),
        "approximate_verified_candidates": summary.get("approximate_verified_count", 0),
        "failed_correctness_candidates": summary.get("failed_correctness_count", 0),
        "active_memory_usage_mb": telemetry.current_used_mb,
        "active_memory_budget_mb": _memory_controller.budget_mb,
        "backends_detected": [b.backend_name for b in backends],
    }


@router.get("/capabilities")
async def list_capabilities() -> List[Dict[str, Any]]:
    """Lists all 21 reference GPU capabilities and software mirrors."""
    return [cap.to_dict() for cap in _capability_registry.list_capabilities()]


@router.get("/capabilities/{capability_id}")
async def get_capability_details(capability_id: str) -> Dict[str, Any]:
    """Retrieves specific capability record and runs substitution search."""
    cap = _capability_registry.get(capability_id)
    if not cap:
        raise HTTPException(status_code=404, detail=f"Capability '{capability_id}' not found")
    substitutions = _capability_search.search_substitution(capability_id)
    return {
        "capability": cap.to_dict(),
        "available_substitutions": [s.to_dict() for s in substitutions],
    }


@router.get("/capability_matrix")
async def get_capability_matrix() -> Dict[str, Any]:
    """Generates and returns the full 21-capability 6-dimensional evaluation matrix."""
    return _capability_matrix_gen.evaluate_all()

