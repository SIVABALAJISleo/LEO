"""
backend/routers/universal_fabric_router.py
==========================================
Universal Replacement Fabric REST API Router.

Provides canonical endpoints:
- GET  /api/hyper/capabilities
- GET  /api/hyper/backends
- POST /api/hyper/execute
- POST /api/hyper/verify
- POST /api/hyper/benchmark
- GET  /api/hyper/certification
- GET  /api/hyper/workloads
"""

from __future__ import annotations

import logging
import time
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

import hyper_phase_change as hpc
from hyper.canonical.verification_state_machine import StrictVerificationRunner

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/hyper", tags=["Universal Replacement Fabric"])


class ExecuteRequest(BaseModel):
    workload_id: str = Field(..., description="Canonical workload identifier, e.g. GEMM_STANDARD")
    policy: str = Field(default="AUTO_VERIFIED", description="CPU_ONLY, VERIFIED_IGPU_ONLY, AUTO_VERIFIED, BENCHMARK_CANDIDATES")
    verify_output: bool = Field(default=True, description="Verify candidate output against independent oracle")
    use_cache: bool = Field(default=True, description="Enable exact semantic multi-operand memoization")
    custom_inputs: Optional[Dict[str, Any]] = Field(default=None, description="Optional custom inputs; if omitted, deterministic canonical inputs are used")


class VerifyRequest(BaseModel):
    workload_id: str = Field(..., description="Workload ID to verify")
    seed: int = Field(default=42, description="PRNG seed for deterministic test inputs")


class BenchmarkRequest(BaseModel):
    workload_id: Optional[str] = Field(default=None, description="Optional specific workload to benchmark; if None, benchmarks full suite")
    policy: str = Field(default="AUTO_VERIFIED", description="Execution policy to evaluate")
    warmup_runs: int = Field(default=2, ge=1, le=10)
    measured_runs: int = Field(default=5, ge=1, le=50)


@router.get("/capabilities")
async def get_capabilities() -> Dict[str, Any]:
    """Returns dynamic hardware discovery, CPU topology, OpenVINO iGPU probe, and RAM footprint."""
    probe = hpc.PhysicalDeviceProbe.run_full_probe()
    registry = hpc.CapabilityRegistry()
    return {
        "status": "SUCCESS",
        "probe": probe.to_dict(),
        "capabilities": registry.to_dict(),
        "fabric_version": hpc.__version__,
    }


@router.get("/backends")
async def get_backends() -> Dict[str, Any]:
    """Lists all mesh backends: CPU, OpenVINO iGPU, and dynamic adapters for IREE, SwiftShader, and PoCL."""
    registry = hpc.CapabilityRegistry()
    return {
        "status": "SUCCESS",
        "backends": [b.to_dict() for b in registry.list_backends()],
    }


@router.get("/workloads")
async def get_workloads() -> Dict[str, Any]:
    """Returns the versioned canonical workload suite with schemas, tolerances, and exactness classes."""
    contracts = hpc.CANONICAL_REGISTRY.get_all_contracts()
    return {
        "status": "SUCCESS",
        "total_canonical_workloads": len(contracts),
        "workloads": [c.to_dict() for c in contracts.values()],
    }


@router.post("/execute")
async def execute_workload(req: ExecuteRequest) -> Dict[str, Any]:
    """
    Executes a workload through the authoritative 11-stage pipeline.
    Fails closed if VERIFIED_IGPU_ONLY is requested and workload cannot run on physical iGPU.
    """
    contract = hpc.CANONICAL_REGISTRY.get_contract(req.workload_id)
    if contract is None:
        raise HTTPException(status_code=404, detail=f"Workload '{req.workload_id}' not found in canonical support contract.")

    # Generate inputs if not supplied
    inputs = req.custom_inputs or StrictVerificationRunner.generate_typical_inputs(req.workload_id, seed=42)

    try:
        policy_enum = hpc.ExecutionPolicy(req.policy)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid policy '{req.policy}'. Valid options: {[p.value for p in hpc.ExecutionPolicy]}",
        )

    try:
        res = hpc.execute_universal_pipeline(
            workload_id=req.workload_id,
            inputs=inputs,
            policy=policy_enum,
            verify_against_reference=req.verify_output,
            use_cache=req.use_cache,
        )
        return {
            "status": "SUCCESS",
            "result": res.to_dict(),
        }
    except hpc.BackendExecutionError as bee:
        logger.warning(f"Backend execution fail-closed: {bee}")
        raise HTTPException(status_code=400, detail=str(bee))
    except Exception as e:
        logger.error(f"Execution error on {req.workload_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/verify")
async def verify_workload(req: VerifyRequest) -> Dict[str, Any]:
    """Runs independent verification against the isolated textbook oracle."""
    contract = hpc.CANONICAL_REGISTRY.get_contract(req.workload_id)
    if contract is None:
        raise HTTPException(status_code=404, detail=f"Workload '{req.workload_id}' not found.")

    inputs = StrictVerificationRunner.generate_typical_inputs(req.workload_id, seed=req.seed)
    # Execute candidate
    cand_out, cand_rec = hpc.CandidateCompiler.execute_candidate(req.workload_id, inputs, contract=contract)
    # Verify candidate against reference
    v_res = hpc.PhaseChangeVerifier.verify_candidate_output(req.workload_id, inputs, cand_out, contract=contract)

    return {
        "status": "SUCCESS",
        "workload_id": req.workload_id,
        "verification": v_res.to_dict(),
        "candidate_telemetry": cand_rec.to_dict(),
    }


@router.post("/benchmark")
async def benchmark_workloads(req: BenchmarkRequest) -> Dict[str, Any]:
    """Executes multi-run empirical benchmarks with warmups, statistics, and regression detection."""
    try:
        policy_enum = hpc.ExecutionPolicy(req.policy)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid policy '{req.policy}'")

    if req.workload_id:
        if req.workload_id not in hpc.CANONICAL_15_WORKLOAD_IDS:
            raise HTTPException(status_code=404, detail=f"Workload '{req.workload_id}' not found.")
        metric = hpc.UniversalFabricBenchmark.benchmark_workload_deep(
            workload_id=req.workload_id,
            policy=policy_enum,
            warmup_runs=req.warmup_runs,
            measured_runs=req.measured_runs,
        )
        return {
            "status": "SUCCESS",
            "metric": metric.to_dict(),
        }
    else:
        suite_report = hpc.UniversalFabricBenchmark.run_full_suite(policy=policy_enum)
        return {
            "status": "SUCCESS",
            "suite_report": suite_report,
        }


@router.get("/certification")
async def get_certification() -> Dict[str, Any]:
    """Evaluates the Seven Acceptance Gates and issues a verifiable Certificate."""
    cert = hpc.FabricCertificationEngine.evaluate_gates()
    return {
        "status": "SUCCESS",
        "certificate": cert.to_dict(),
    }
