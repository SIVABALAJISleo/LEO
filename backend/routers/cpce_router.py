"""
backend/routers/cpce_router.py
==============================
FastAPI Router for HYPER Computational Phase-Change Engine (CPCE).
Prefix: /api/v1/cpce
Tags: ["Computational Phase-Change Engine"]
"""

from __future__ import annotations

import time
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
import numpy as np

from hyper_x.cpce import (
    ComputationalPhaseChangeEngine,
    WorkloadContract,
    ValidationMode,
    ExactnessRequirement,
    SearchBudget,
)

router = APIRouter(prefix="/api/v1/cpce", tags=["Computational Phase-Change Engine"])

# Master CPCE Singleton
cpce_engine = ComputationalPhaseChangeEngine()


class ExecuteRequest(BaseModel):
    contract_id: str = Field(default="dense_gemm")
    inputs: Dict[str, Any] = Field(default_factory=dict)
    use_cache: bool = True
    max_search_time_ms: float = 500.0


class SearchRequest(BaseModel):
    contract_id: str = Field(default="dense_gemm")
    inputs: Dict[str, Any] = Field(default_factory=dict)
    max_candidates: int = 5
    max_search_time_ms: float = 500.0


@router.get("/status")
def get_cpce_status():
    """Returns runtime health, physical device detection, cache statistics, and support matrix."""
    return cpce_engine.get_status()


@router.get("/contracts")
def list_contracts():
    """Lists all registered workload contracts."""
    return cpce_engine.contracts.list_contracts()


@router.get("/support-matrix")
def get_support_matrix():
    """Returns the versioned machine-readable support matrix."""
    return {
        "summary": cpce_engine.support_matrix.compute_summary_metrics(),
        "workloads": cpce_engine.support_matrix.list_entries(),
    }


@router.post("/search")
def search_candidate_pathways(req: SearchRequest):
    """Searches and ranks valid candidate execution plans under contract constraints."""
    contract = cpce_engine.contracts.get(req.contract_id)
    if contract is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contract '{req.contract_id}' not found.",
        )

    # Reconstruct inputs
    proc_inputs: Dict[str, Any] = {}
    if "A" in req.inputs and "B" in req.inputs:
        proc_inputs["A"] = np.asarray(req.inputs["A"], dtype=np.float32)
        proc_inputs["B"] = np.asarray(req.inputs["B"], dtype=np.float32)
        graph = cpce_engine.build_canonical_graph_for_gemm(proc_inputs["A"], proc_inputs["B"])
    else:
        proc_inputs = req.inputs
        graph = cpce_engine.build_canonical_graph_for_gemm(np.ones((64, 64)), np.ones((64, 64)))

    budget = SearchBudget(max_candidates=req.max_candidates, max_search_time_ms=req.max_search_time_ms)
    candidates = cpce_engine.search_engine.search_plans(graph, contract, budget=budget)
    return {
        "contract_id": req.contract_id,
        "candidate_count": len(candidates),
        "candidates": [c.to_dict() for c in candidates],
    }


@router.post("/execute")
def execute_workload(req: ExecuteRequest):
    """
    Executes a workload through the CPCE pipeline with independent verification and provenance sealing.
    """
    contract = cpce_engine.contracts.get(req.contract_id)
    if contract is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contract '{req.contract_id}' not found.",
        )

    # Process array inputs if present
    proc_inputs: Dict[str, Any] = {}
    if "A" in req.inputs and "B" in req.inputs:
        proc_inputs["A"] = np.asarray(req.inputs["A"], dtype=np.float32)
        proc_inputs["B"] = np.asarray(req.inputs["B"], dtype=np.float32)
        ref_fn = lambda inp: np.matmul(inp["A"], inp["B"])
    elif "coefficients" in req.inputs and "x" in req.inputs:
        proc_inputs["coefficients"] = np.asarray(req.inputs["coefficients"], dtype=np.float64)
        proc_inputs["x"] = float(req.inputs["x"])
        # Reference direct polynomial evaluation: sum(c_i * x^i)
        ref_fn = lambda inp: sum(c * (inp["x"] ** i) for i, c in enumerate(inp["coefficients"]))
    else:
        proc_inputs = req.inputs
        ref_fn = None

    budget = SearchBudget(max_search_time_ms=req.max_search_time_ms)
    try:
        res = cpce_engine.execute_workload(
            contract_id=req.contract_id,
            inputs=proc_inputs,
            reference_fn=ref_fn,
            use_cache=req.use_cache,
            search_budget=budget,
        )
        return res.to_dict()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"CPCE execution failed: {e}",
        )
