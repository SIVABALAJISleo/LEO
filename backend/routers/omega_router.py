"""
backend/routers/omega_router.py
===============================
FastAPI Router for HYPER Ω Autonomous Computational Discovery & Proof Architecture.

Exposes:
- POST /api/v1/omega/run             : Runs the full Section 59 Master Loop
- POST /api/v1/omega/escape          : Evaluates 7 Counterfactual Escape Classes
- POST /api/v1/omega/duel            : Executes BreakthroughAgent vs FalsificationAgent duel
- GET  /api/v1/omega/knowledge_graph : Retrieves Knowledge Graph & pattern index
- GET  /api/v1/omega/theorems        : Formal equivalence theorems & proof status
- GET  /api/v1/omega/counterexamples : Minimal counterexamples & failure-derived search constraints
- GET  /api/v1/omega/gate_status     : Current UniversalClaimGate 12-checkpoint audit
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
import numpy as np

from hyper_universal.contract_ir import ContractIR, ContractType
from hyper_universal.workload import UniversalWorkload, WorkloadFamily
from hyper_universal.types import ResultTaxonomy
from hyper_omega.orchestrator import HyperOmegaOrchestrator
from hyper_omega.instant_path.engine import ExecutionMode

router = APIRouter(prefix="/api/v1/omega", tags=["HYPER Ω Discovery & Proof Engine"])

_orchestrator = HyperOmegaOrchestrator()


def _sanitize_for_json(obj: Any) -> Any:
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, np.generic):
        return obj.item()
    if hasattr(obj, "dict"):
        return _sanitize_for_json(obj.dict())
    if isinstance(obj, dict):
        return {k: _sanitize_for_json(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_sanitize_for_json(v) for v in obj]
    return obj


class OmegaRunRequest(BaseModel):
    workload_id: str = "bilinear_matrix_multiplication_2x2"
    contract_type: str = "EXACT"
    mode: str = "ONLINE_EXECUTION"  # ONLINE_EXECUTION | OFFLINE_RESEARCH


@router.post("/run")
def run_omega_pipeline(req: OmegaRunRequest) -> Dict[str, Any]:
    """Runs the full HYPER Ω discovery, verification, falsification, and proof pipeline."""
    c_type = getattr(ContractType, req.contract_type, ContractType.EXACT)
    contract = ContractIR(contract_type=c_type)
    workload = UniversalWorkload(
        workload_id=req.workload_id,
        name=req.workload_id.replace("_", " ").title(),
        workload_family=WorkloadFamily.LINEAR_ALGEBRA,
        contract=contract,
        input_schema={"A": (2, 2), "B": (2, 2)},
    )
    exec_mode = ExecutionMode.OFFLINE_RESEARCH if req.mode == "OFFLINE_RESEARCH" else ExecutionMode.ONLINE_EXECUTION

    nominal_inputs = [
        (np.array([[1.0, 2.0], [3.0, 4.0]]), np.array([[5.0, 6.0], [7.0, 8.0]])),
        (np.array([[0.5, -1.0], [2.0, 3.5]]), np.array([[1.2, 0.0], [-0.5, 4.0]])),
    ]
    ref_fn = lambda inp: inp[0] @ inp[1]

    summary = _orchestrator.run_full_omega_loop(
        workload=workload,
        contract=contract,
        nominal_inputs=nominal_inputs,
        reference_fn=ref_fn,
        mode=exec_mode
    )

    return {
        "status": "success",
        "workload_id": summary.workload_id,
        "dispatch_path": summary.instant_path_dispatch,
        "final_status": summary.final_status.value,
        "theorems_discovered": summary.theorems_discovered,
        "counterexamples_recorded": summary.counterexamples_recorded,
        "active_search_constraints": summary.active_search_constraints,
        "wall_time_seconds": summary.wall_time_seconds,
        "claim_certificate": _sanitize_for_json(summary.claim_certificate.dict()),
    }


@router.get("/knowledge_graph")
def get_knowledge_graph() -> Dict[str, Any]:
    """Returns the Universal Computational Knowledge Graph nodes and patterns."""
    nodes = _orchestrator.instant_path.knowledge_graph.nodes
    return {
        "total_nodes": len(nodes),
        "patterns": [
            {
                "node_id": n.node_id,
                "pattern_signature": n.pattern_signature,
                "known_theorem": n.known_theorem_id,
                "known_transformation": n.known_transformation_id,
                "algorithm_family": n.algorithm_family,
                "verification_status": n.verification_status,
                "historical_speedup": n.speedup_record,
            }
            for n in nodes.values()
        ]
    }


@router.get("/theorems")
def get_theorems() -> Dict[str, Any]:
    """Returns the catalog of formal equivalence theorems and their proof states."""
    thms = _orchestrator.theorem_engine.theorems
    return {
        "theorems_count": len(thms),
        "theorems": [
            {
                "theorem_id": t.theorem_id,
                "conjecture": t.conjecture,
                "status": t.status.value,
                "precondition": t.precondition_P,
                "contract": t.contract_C,
                "proof_obligations": t.proof_obligations,
                "proof_artifact": t.proof_artifact,
            }
            for t in thms.values()
        ]
    }


@router.get("/counterexamples")
def get_counterexamples() -> Dict[str, Any]:
    """Returns stored minimal counterexamples and derived negative search constraints."""
    cx_list = _orchestrator.counterexample_db.counterexamples
    cst_list = _orchestrator.counterexample_db.derived_constraints
    return {
        "total_counterexamples": len(cx_list),
        "active_constraints_count": len(cst_list),
        "counterexamples": [
            {
                "candidate_id": c.candidate_id,
                "failure_type": c.failure_type,
                "failed_contract": c.failed_contract,
                "failed_assumption": c.failed_assumption,
                "severity": c.severity,
            }
            for c in cx_list
        ],
        "active_constraints": [
            {
                "constraint_id": c.constraint_id,
                "disallowed_transformation": c.disallowed_transformation,
                "learned_rule": c.learned_rule,
            }
            for c in cst_list
        ]
    }


@router.get("/gate_status")
def get_gate_status() -> Dict[str, Any]:
    """Returns the current UniversalClaimGate audit certificates."""
    certs = _orchestrator.claim_gate.issued_certificates
    latest = certs[-1] if certs else None
    return {
        "total_certificates_issued": len(certs),
        "latest_certificate": _sanitize_for_json(latest.dict()) if latest else None
    }


@router.get("/dormant_silicon")
def get_dormant_silicon() -> Dict[str, Any]:
    """Returns dormant on-die silicon acceleration engines harvested on host (VNNI, DP4A, GNA 3.0, USM)."""
    from hyper_omega.hardware_bridge import DormantSiliconHarvester
    harvester = DormantSiliconHarvester()
    return {
        "summary": harvester.get_summary(),
        "engines": [
            {
                "name": e.name,
                "location": e.silicon_location,
                "status": e.status,
                "instruction_set": e.instruction_set,
                "theoretical_tops": e.theoretical_tops,
                "power_watts": e.power_watts,
                "description": e.description,
            }
            for e in harvester.engines.values()
        ]
    }


@router.get("/micro_hardware")
def get_micro_hardware() -> Dict[str, Any]:
    """Returns ultra-low-cost micro-hardware co-processor options ($15-$35) vs RTX 5090 comparison."""
    from hyper_omega.hardware_bridge import MicroHardwareCatalog
    options = MicroHardwareCatalog.get_options()
    rtx_comp = MicroHardwareCatalog.get_rtx_5090_comparison()
    return {
        "rtx_5090_reference": rtx_comp,
        "micro_hardware_options": [
            {
                "name": opt.name,
                "form_factor": opt.form_factor,
                "cost_usd": opt.cost_usd,
                "int8_tops": opt.int8_tops,
                "power_watts": opt.power_watts,
                "cost_per_tops": opt.cost_per_tops,
                "frameworks": opt.supported_frameworks,
                "description": opt.description,
            }
            for opt in options
        ]
    }


class ComplexityCollapseRequest(BaseModel):
    problem_size: int = 4096
    rank_k: int = 64


@router.post("/complexity_collapse")
def evaluate_complexity_collapse(req: ComplexityCollapseRequest) -> Dict[str, Any]:
    """Evaluates the Big-O complexity collapse proving hardware disadvantage irrelevance."""
    from hyper_omega.hardware_bridge import SoftwareDefinedVirtualSilicon
    sdvs = SoftwareDefinedVirtualSilicon()
    report = sdvs.evaluate_complexity_collapse(problem_size=req.problem_size, rank_k=req.rank_k)
    return {
        "physical_hardware_claimed": report.physical_hardware_claimed,
        "physical_hardware_status": report.physical_hardware_status,
        "unlocked_on_die_tops": report.unlocked_on_die_tops,
        "active_on_die_engines": report.active_on_die_engines,
        "zero_copy_usm_latency_ms": report.zero_copy_usm_latency_ms,
        "baseline_brute_force_ops": report.baseline_brute_force_ops,
        "escaped_algorithm_ops": report.escaped_algorithm_ops,
        "work_elimination_factor": report.work_elimination_factor,
        "effective_rtx_speedup_equivalent": report.effective_rtx_speedup_equivalent,
        "application_contract_parity_pct": report.application_contract_parity_pct,
        "hardware_disadvantage_irrelevance_pct": report.hardware_disadvantage_irrelevance_pct,
        "conclusion": report.conclusion,
    }


@router.get("/universal_closure")
def get_universal_closure() -> Dict[str, Any]:
    """Evaluates and returns the Universal Metamorphic Closure verdict (100% Contract Completeness)."""
    from hyper_omega.universal_closure import UniversalWorkloadClosureEngine
    engine = UniversalWorkloadClosureEngine()
    verdict = engine.evaluate_universal_closure(num_samples=40)
    return {
        "universal_contract_completeness_pct": verdict.universal_contract_completeness_pct,
        "total_workloads_evaluated": verdict.total_workloads_evaluated,
        "total_contracts_satisfied": verdict.total_contracts_satisfied,
        "alpha_regime_ratio": verdict.alpha_regime_ratio,
        "beta_regime_ratio": verdict.beta_regime_ratio,
        "gamma_regime_ratio": verdict.gamma_regime_ratio,
        "closure_theorem_verified": verdict.closure_theorem_verified,
        "physical_hardware_equivalence": verdict.physical_hardware_equivalence,
        "hardware_disadvantage_irrelevance_pct": verdict.hardware_disadvantage_irrelevance_pct,
        "closure_status": verdict.closure_status,
        "proof_basis": verdict.proof_basis,
    }


