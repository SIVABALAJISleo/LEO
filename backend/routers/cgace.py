"""
backend/routers/cgace.py
=============================================================================
FastAPI Router for Contract-Gated Adaptive Computation Elimination (C-GACE)
=============================================================================
"""

import time
import numpy as np
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException

from core_ai.c_gace_engine import global_cgace_engine, ExecutionContract

router = APIRouter(prefix="/api/v1/cgace", tags=["C-GACE Engine"])


class CGACEExecuteRequest(BaseModel):
    workload_type: str = Field("matrix_gemm", description="matrix_gemm, text_llm, spectral_fft, simulation, ternary_layer")
    error_bound_eps: float = Field(0.01, ge=0.0001, le=0.5)
    perceptual_threshold: float = Field(0.95, ge=0.5, le=1.0)
    max_latency_ms: float = Field(50.0, ge=0.1)
    matrix_dim: Optional[int] = Field(256, ge=16, le=1024)
    prompt_text: Optional[str] = Field("the quick brown fox jumps over the lazy dog and the quick brown fox")
    force_level: Optional[int] = Field(None, ge=0, le=6)


@router.post("/execute")
async def execute_cgace(req: CGACEExecuteRequest):
    """
    Dispatches compute task through the C-GACE multi-level cheap-path pipeline.
    """
    contract = ExecutionContract(
        metric="relative_l2_error" if req.workload_type != "text_llm" else "token_match",
        error_bound_eps=req.error_bound_eps,
        perceptual_threshold=req.perceptual_threshold,
        max_latency_ms=req.max_latency_ms
    )

    if req.workload_type == "matrix_gemm":
        rng = np.random.RandomState(42)
        dim = req.matrix_dim or 256
        # Generate structured rank-16 matrix
        U = rng.randn(dim, 16).astype(np.float32)
        V = rng.randn(16, dim).astype(np.float32)
        A = U @ V + rng.randn(dim, dim).astype(np.float32) * 0.0001
        B = rng.randn(dim, dim).astype(np.float32)
        
        res = global_cgace_engine.execute_with_contract(
            workload_type="matrix_gemm",
            input_data=A,
            contract=contract,
            secondary_data=B,
            force_level=req.force_level
        )
    elif req.workload_type == "text_llm":
        res = global_cgace_engine.execute_with_contract(
            workload_type="text_llm",
            input_data=req.prompt_text or "the quick brown fox jumps",
            contract=contract,
            force_level=req.force_level
        )
    elif req.workload_type == "spectral_fft":
        N = 1024
        t = np.arange(N)
        sig = np.sin(2 * np.pi * 35 * t / N) + 0.6 * np.cos(2 * np.pi * 105 * t / N)
        res = global_cgace_engine.execute_with_contract(
            workload_type="spectral_fft",
            input_data=sig,
            contract=contract,
            force_level=req.force_level
        )
    elif req.workload_type == "ternary_layer":
        x = np.random.randn(128).astype(np.float32)
        res = global_cgace_engine.execute_with_contract(
            workload_type="ternary_layer",
            input_data=x,
            contract=contract,
            force_level=req.force_level
        )
    else:
        # Default simulation state
        state = np.random.randn(64, 3).astype(np.float32)
        res = global_cgace_engine.execute_with_contract(
            workload_type="simulation",
            input_data=state,
            contract=contract,
            force_level=req.force_level
        )

    # Sanitize numpy arrays for JSON serialization
    clean_res = dict(res)
    if isinstance(clean_res.get("result"), np.ndarray):
        clean_res["result"] = f"ndarray(shape={clean_res['result'].shape}, dtype={clean_res['result'].dtype})"

    return {
        "workload_type": req.workload_type,
        "contract": {
            "metric": contract.metric,
            "error_bound_eps": contract.error_bound_eps,
            "perceptual_threshold": contract.perceptual_threshold,
            "max_latency_ms": contract.max_latency_ms
        },
        "pipeline_result": clean_res,
    }


@router.post("/falsify")
async def trigger_self_falsification():
    """
    Executes the self-falsification loop over adversarial test sets.
    """
    return global_cgace_engine.run_self_falsification_audit()


@router.get("/telemetry")
async def get_cgace_telemetry():
    """
    Returns runtime telemetry, promoted paths, and average work eliminated.
    """
    return global_cgace_engine.get_telemetry()
