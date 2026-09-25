"""
backend/routers/pathway_router.py
=================================
FastAPI router for Verified Computational Pathway Discovery Engine.

Endpoints:
- POST /api/v1/pathway/analyze
- POST /api/v1/pathway/search
- POST /api/v1/pathway/verify
- POST /api/v1/pathway/execute
- POST /api/v1/pathway/benchmark
- POST /api/v1/pathway/adversarial
- GET /api/v1/pathway/{id}
- GET /api/v1/pathway/{id}/proof
- GET /api/v1/pathway/{id}/trace
- GET /api/v1/parity/report
"""

from __future__ import annotations

import dataclasses
import os
import time
import uuid
from typing import Any, Dict, List, Optional

import numpy as np
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import HTMLResponse
import os
from pydantic import BaseModel, Field

from hyper.discovery.adversarial import AdversarialWorkloadGenerator, WorkloadCategory
from hyper.discovery.cir import CIRGraph, CIRTensorMeta, DataType, OpType
from hyper.discovery.contract import VerificationMode, WorkloadContract
from hyper.discovery.engine import EngineExecutionReport, VerifiedPathwayEngine
from hyper.discovery.search import SearchConfig, SearchStrategy

router = APIRouter(prefix="/api/v1/pathway", tags=["Pathway Discovery"])
parity_router = APIRouter(prefix="/api/v1/parity", tags=["Parity Audit"])

# Shared master engine singleton
engine = VerifiedPathwayEngine()

# Registry for stored pathways, proofs, and execution traces
STORED_REPORTS: Dict[str, EngineExecutionReport] = {}

DASHBOARD_FILE = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "dashboard", "pathway_discovery_dashboard.html")
)


@router.get("/dashboard", response_class=HTMLResponse)
async def get_pathway_dashboard():
    """Serve research-grade Pathway Discovery Engine dashboard."""
    if os.path.exists(DASHBOARD_FILE):
        with open(DASHBOARD_FILE, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>Pathway Dashboard HTML not found</h1>", status_code=404)


class WorkloadSubmitRequest(BaseModel):
    workload_name: str = Field(..., example="chained_gemm")
    graph: Dict[str, Any]
    inputs: Dict[str, Any]
    contract: Optional[Dict[str, Any]] = None
    unknown_workload_mode: bool = False
    strategy: str = "A_STAR"
    max_candidates: int = 20
    benchmark_repetitions: int = 5


class VerifyRequest(BaseModel):
    workload_name: str
    candidate_graph: Dict[str, Any]
    reference_graph: Dict[str, Any]
    inputs: Dict[str, Any]
    contract: Dict[str, Any]


class AdversarialRequest(BaseModel):
    category: str = "BLIND_HOLDOUT_SET"
    adversarial_type: Optional[str] = "PRIME_DIMENSIONS"


@router.post("/analyze")
async def analyze_workload(req: WorkloadSubmitRequest):
    """Analyze a computational problem graph, predicting FLOPs, traffic, and scheduling."""
    try:
        g = CIRGraph.from_dict(req.graph)
        pred = engine.cost_model.predict_cost(g)
        sched = engine.scheduler.schedule_workload(g)
        return {
            "workload_name": req.workload_name,
            "predicted_cost": pred.to_dict(),
            "scheduling_decision": dataclasses.asdict(sched),
            "total_nodes": len(g.nodes),
            "total_edges": len(g.edges),
            "estimated_flops": g.total_estimated_flops(),
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/search")
async def search_pathway(req: WorkloadSubmitRequest):
    """Execute bounded search over alternative computational pathways."""
    try:
        g = CIRGraph.from_dict(req.graph)
        inputs = _deserialize_inputs(req.inputs)
        contract = (
            WorkloadContract.from_dict(req.contract)
            if req.contract
            else WorkloadContract(
                contract_id=f"c_{req.workload_name}",
                workload_name=req.workload_name,
                required_outputs=[g.nodes[oid].name for oid in g.outputs],
                exactness_mode=VerificationMode.MODE_2_NUMERIC_EXACT,
            )
        )

        cfg = SearchConfig(
            strategy=SearchStrategy(req.strategy) if req.strategy in SearchStrategy.__members__ else SearchStrategy.A_STAR,
            max_candidates=req.max_candidates,
        )

        res = engine.search_engine.discover(
            initial_graph=g,
            sample_inputs=inputs,
            contract=contract,
            config=cfg,
        )

        return res.to_dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/verify")
async def verify_pathway(req: VerifyRequest):
    """Independently verify a candidate pathway against trusted reference."""
    try:
        cand_g = CIRGraph.from_dict(req.candidate_graph)
        ref_g = CIRGraph.from_dict(req.reference_graph)
        inputs = _deserialize_inputs(req.inputs)
        contract = WorkloadContract.from_dict(req.contract)

        passed, vrecord, audit = engine.verifier.verify_candidate(
            candidate_graph=cand_g,
            reference_graph=ref_g,
            inputs=inputs,
            contract=contract,
        )

        return {
            "passed": passed,
            "verification_record": vrecord.to_dict(),
            "contract_audit": audit.to_dict(),
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/execute")
async def execute_and_discover(req: WorkloadSubmitRequest):
    """Execute end-to-end verified discovery, proof generation, and benchmarking."""
    try:
        g = CIRGraph.from_dict(req.graph)
        inputs = _deserialize_inputs(req.inputs)
        contract = (
            WorkloadContract.from_dict(req.contract)
            if req.contract
            else WorkloadContract(
                contract_id=f"c_{req.workload_name}",
                workload_name=req.workload_name,
                required_outputs=[g.nodes[oid].name for oid in g.outputs],
                exactness_mode=VerificationMode.MODE_2_NUMERIC_EXACT,
            )
        )

        report = engine.process_workload(
            graph=g,
            inputs=inputs,
            contract=contract,
            unknown_workload_mode=req.unknown_workload_mode,
            benchmark_repetitions=req.benchmark_repetitions,
        )

        report_id = f"pw_{uuid.uuid4().hex[:10]}"
        STORED_REPORTS[report_id] = report

        res_dict = report.to_dict()
        res_dict["pathway_id"] = report_id
        return res_dict
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/benchmark")
async def benchmark_workload(req: WorkloadSubmitRequest):
    """Run dedicated multi-repetition benchmark on candidate graph."""
    try:
        g = CIRGraph.from_dict(req.graph)
        inputs = _deserialize_inputs(req.inputs)
        stats = engine.benchmarker.run_benchmark(
            graph=g,
            inputs=inputs,
            repetitions=req.benchmark_repetitions,
            warmup=2,
        )
        return stats.to_dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/adversarial")
async def run_adversarial_challenge(req: AdversarialRequest):
    """Generate and test an adversarial workload designed to defeat shortcuts."""
    try:
        cat = WorkloadCategory(req.category)
        adv_gen = engine.adversarial_gen

        if req.adversarial_type == "PRIME_DIMENSIONS":
            adv = adv_gen.generate_prime_dimensions_gemm(cat)
        elif req.adversarial_type == "CATASTROPHIC_CANCELLATION":
            adv = adv_gen.generate_catastrophic_cancellation(cat)
        elif req.adversarial_type == "ULTRA_SPARSE":
            adv = adv_gen.generate_ultra_sparse(cat)
        elif req.adversarial_type == "MEMORY_BOUND":
            adv = adv_gen.generate_memory_bound_streaming(cat)
        else:
            adv = adv_gen.generate_prime_dimensions_gemm(cat)

        report = engine.process_workload(
            graph=adv.graph,
            inputs=adv.sample_inputs,
            contract=adv.contract,
            unknown_workload_mode=True,
            benchmark_repetitions=3,
        )

        return {
            "adversarial_workload": adv.to_dict(),
            "execution_report": report.to_dict(),
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{pathway_id}")
async def get_pathway(pathway_id: str):
    """Retrieve full execution report for a discovered pathway."""
    if pathway_id not in STORED_REPORTS:
        raise HTTPException(status_code=404, detail=f"Pathway ID '{pathway_id}' not found.")
    return STORED_REPORTS[pathway_id].to_dict()


@router.get("/{pathway_id}/proof")
async def get_pathway_proof(pathway_id: str):
    """Retrieve machine-readable proof record and human-readable explanation."""
    if pathway_id not in STORED_REPORTS:
        raise HTTPException(status_code=404, detail=f"Pathway ID '{pathway_id}' not found.")
    return STORED_REPORTS[pathway_id].proof_record.to_dict()


@router.get("/{pathway_id}/trace")
async def get_pathway_trace(pathway_id: str):
    """Retrieve auditable search trace showing candidate rejection/acceptance history."""
    if pathway_id not in STORED_REPORTS:
        raise HTTPException(status_code=404, detail=f"Pathway ID '{pathway_id}' not found.")
    rep = STORED_REPORTS[pathway_id]
    return {
        "workload_id": rep.workload_id,
        "is_shortcut_found": rep.is_shortcut_found,
        "speedup": rep.proof_record.speedup,
        "pathway_ascii_diff": rep.proof_record.pathway_ascii_diff,
    }


@parity_router.get("/report")
async def get_parity_report():
    """Retrieve current research-grade parity scorecard."""
    return {
        "statement": "SCIENTIFIC NOTICE: Hardware parity is not claimed. CPU+iGPU execution is measured locally.",
        "hardware_parity": "NO_HARDWARE_PARITY",
        "supported_verification_modes": [m.value for m in VerificationMode],
        "stored_evaluations_count": len(STORED_REPORTS),
        "timestamp": time.time(),
    }


def _deserialize_inputs(raw: Dict[str, Any]) -> Dict[str, Any]:
    out = {}
    for k, v in raw.items():
        if isinstance(v, list):
            out[k] = np.array(v, dtype=np.float32)
        elif isinstance(v, dict) and "data" in v:
            out[k] = np.array(v["data"], dtype=v.get("dtype", "float32"))
        elif isinstance(v, np.ndarray):
            out[k] = v
        else:
            out[k] = v
    return out
