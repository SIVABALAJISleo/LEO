"""
backend/routers/universal_router.py
===================================
REST API Router for the Universal Computational Parity Engine (UCPE).

Endpoints:
- POST /api/v1/universal/analyze     : Analyzes workload & probes information boundary
- POST /api/v1/universal/search      : Runs full adaptive pathway search pipeline
- POST /api/v1/universal/generate    : Generates 10-family candidate pathways
- POST /api/v1/universal/verify      : Runs independent multi-strategy verification
- POST /api/v1/universal/benchmark   : Runs representative multi-domain benchmark
- POST /api/v1/universal/synthesize  : Synthesizes sandboxed computational program
- GET  /api/v1/universal/status      : System and search saturation status
- GET  /api/v1/universal/pathways    : Registered pathways and structural hashes
- GET  /api/v1/universal/frontier    : Active multi-objective Pareto frontier
- GET  /api/v1/universal/scorecard   : Universal Parity Scorecard (HYPER vs RTX 5090)
- GET  /api/v1/universal/experiments : Experiment history
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
import numpy as np

from hyper.universal import (
    UniversalComputationalParityEngine,
    UniversalWorkload,
    UniversalWorkloadAdapter,
    UniversalContract,
    ContractCorrectness,
    PrecisionTier,
    WorkloadDomain,
    ProgramSynthesizer,
    UniversalWorkloadSuite,
    AdversarialWorkloadGenerator,
)

router = APIRouter(prefix="/api/v1/universal", tags=["Universal Computational Parity Engine (UCPE)"])

_engine = UniversalComputationalParityEngine()


def _sanitize_for_json(obj: Any) -> Any:
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, np.generic):
        return obj.item()
    if isinstance(obj, dict):
        return {k: _sanitize_for_json(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_sanitize_for_json(v) for v in obj]
    return obj


class UniversalSearchRequest(BaseModel):
    workload_domain: str = "POLYNOMIAL" # "POLYNOMIAL" | "SORTING" | "MATRIX" | "UNSEEN" | "ADVERSARIAL_NOISE"
    dimension: int = 100
    max_candidates: int = 15
    max_time_seconds: float = 20.0
    contract_exactness: str = "EXACT"


class UniversalVerifyRequest(BaseModel):
    candidate_output: List[float]
    reference_output: List[float]
    tolerance: float = 0.0
    verification_method: str = "EXACT"


class SynthesizeRequest(BaseModel):
    operation: str = "sum" # "sum", "mean", "min", "max"


@router.post("/search")
async def universal_search(req: UniversalSearchRequest) -> Dict[str, Any]:
    """Runs the full universal adaptive discovery and verification pipeline."""
    dom = req.workload_domain.upper()

    if dom == "POLYNOMIAL":
        wl, c = UniversalWorkloadSuite.get_polynomial_workload(degree=10, num_points=req.dimension)
    elif dom == "SORTING":
        wl, c = UniversalWorkloadSuite.get_sorting_workload(N=req.dimension, key_max=500)
    elif dom == "MATRIX":
        wl, c = UniversalWorkloadSuite.get_matrix_workload(dim=min(req.dimension, 128))
    elif dom == "ADVERSARIAL_NOISE":
        wl, c = AdversarialWorkloadGenerator.get_incompressible_noise_workload(size=req.dimension)
    else:
        wl, c = UniversalWorkloadSuite.generate_unseen_workload()

    res = _engine.run_universal_pipeline(
        workload_target=wl,
        sample_input=wl.sample_input,
        contract=c,
        max_candidates=req.max_candidates,
        max_time_seconds=req.max_time_seconds,
    )
    return _sanitize_for_json(res)


@router.post("/analyze")
async def universal_analyze(req: UniversalSearchRequest) -> Dict[str, Any]:
    """Inspects an arbitrary workload and extracts its contract & information boundaries."""
    if req.workload_domain.upper() == "SORTING":
        wl, c = UniversalWorkloadSuite.get_sorting_workload(N=req.dimension)
    else:
        wl, c = UniversalWorkloadSuite.get_polynomial_workload(degree=10, num_points=req.dimension)

    from hyper.universal.information import InformationBoundaryEngine
    profile = InformationBoundaryEngine.analyze(wl, c)
    return _sanitize_for_json({
        "workload": wl.to_dict(),
        "contract": c.to_dict(),
        "information_boundary": profile.to_dict(),
    })


@router.post("/verify")
async def universal_verify(req: UniversalVerifyRequest) -> Dict[str, Any]:
    """Independently verifies candidate output using the Master Verifier."""
    cand = np.array(req.candidate_output, dtype=np.float32)
    ref = np.array(req.reference_output, dtype=np.float32)
    c = UniversalContract(
        contract_id="manual_verify",
        workload_id="manual_wl",
        correctness=ContractCorrectness.EXACT if req.tolerance == 0.0 else ContractCorrectness.NUMERICAL,
        numeric_tolerance=req.tolerance,
        verification_method=req.verification_method,
    )
    v_res = _engine.verifier.verify(cand, ref, c)
    return v_res.to_dict()


@router.post("/synthesize")
async def universal_synthesize(req: SynthesizeRequest) -> Dict[str, Any]:
    """Synthesizes a verified computational program kernel using AST-sandboxed templates."""
    pathway = ProgramSynthesizer.synthesize_reduction_pathway(req.operation)
    return pathway.to_dict()


@router.get("/status")
async def universal_status() -> Dict[str, Any]:
    """Returns current engine status, diversity statistics, and active hardware topology."""
    return {
        "hardware": "Intel Core i5-12450H (4P + 4E) + Intel UHD Graphics (48 EU) + 16GB RAM",
        "diversity_stats": _engine.diversity_engine.get_stats(),
        "pareto_points_count": len(_engine.frontier.points),
        "total_experiments_run": len(_engine.experiments_history),
        "rtx5090_reference_spec": _engine.rtx_model.to_dict(),
    }


@router.get("/frontier")
async def universal_frontier() -> List[Dict[str, Any]]:
    """Returns the current multi-objective Pareto frontier."""
    return _engine.frontier.to_list()


@router.get("/pathways")
async def universal_pathways() -> List[Dict[str, Any]]:
    """Returns all registered unique pathways."""
    return [p.to_dict() for p in _engine.diversity_engine.get_all()]


@router.get("/experiments")
async def universal_experiments() -> List[Dict[str, Any]]:
    """Returns recent experiment runs."""
    return _engine.experiments_history[-20:]
