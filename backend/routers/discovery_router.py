"""
backend/routers/discovery_router.py
===================================
FastAPI Router for UCTDE: Universal Computational Discovery Lab.
"""

from __future__ import annotations
import time
from typing import Any, Dict, List, Optional
import numpy as np
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from hyper.discovery.engine import UniversalComputationalDiscoveryEngine
from hyper.discovery.hypotheses import EpistemicState

router = APIRouter(prefix="/api/v1/discovery", tags=["discovery"])
_engine = UniversalComputationalDiscoveryEngine()


def _sanitize_for_json(obj: Any) -> Any:
    """Recursively converts NumPy data types into JSON-serializable primitives."""
    if isinstance(obj, dict):
        return {str(k): _sanitize_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple, set)):
        return [_sanitize_for_json(item) for item in obj]
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, (np.floating, np.float32, np.float64)):
        return float(obj)
    elif isinstance(obj, (np.integer, np.int32, np.int64)):
        return int(obj)
    elif isinstance(obj, (np.bool_, bool)):
        return bool(obj)
    return obj


class AnalyzeWorkloadRequest(BaseModel):
    name: str = "PolynomialEvaluation"
    domain: str = "NUMERICAL_POLYNOMIAL"
    degree: int = 16
    points_count: int = 500


class ProveClaimRequest(BaseModel):
    claim_type: str = "polynomial_horner"
    degree: int = 16


class CounterexampleAttackRequest(BaseModel):
    domain: str = "BOUNDED_SORTING"
    hypothesis_id: str = "hyp-sorting-linear"


class SearchDiscoveryRequest(BaseModel):
    workload_name: str = "PolynomialDegree32"
    domain: str = "NUMERICAL_POLYNOMIAL"
    max_candidates: int = 10


@router.get("/status")
def get_discovery_status() -> Dict[str, Any]:
    """Retrieves target status, epistemic breakdown, and discovery totals."""
    status = _engine.get_target_status()
    kg_summary = _engine.get_knowledge_graph_summary()
    return _sanitize_for_json({
        "status": "ONLINE",
        "engine": "Universal Computational Discovery Engine (UCTDE)",
        "target_status": status,
        "knowledge_graph": {
            "node_count": kg_summary["node_count"],
            "edge_count": kg_summary["edge_count"],
        },
        "counterexamples_discovered": len(_engine.get_counterexamples()),
        "proofs_established": len(_engine.get_proofs()),
        "rules_in_library": len(_engine.get_rules()),
        "timestamp": time.time(),
    })


@router.post("/search")
def run_discovery_search(req: SearchDiscoveryRequest) -> Dict[str, Any]:
    """Executes a full discovery cycle over a canonical or synthesized workload."""
    if req.domain == "NUMERICAL_POLYNOMIAL":
        coeffs = np.linspace(0.1, 1.0, 17, dtype=np.float32)
        sample = np.linspace(-1.0, 1.0, 200, dtype=np.float32)
        def poly_fn(x):
            res = np.zeros_like(x)
            for i, c in enumerate(coeffs):
                res += c * (x ** i)
            return res
        fn = poly_fn
    elif req.domain in ("SORTING", "BOUNDED_SORTING"):
        sample = np.random.randint(0, 100, size=500, dtype=np.int32)
        fn = lambda arr: np.sort(arr)
    else:
        sample = np.random.randn(64, 64).astype(np.float32)
        fn = lambda mat: mat @ mat

    meta_extra = {"coeffs": coeffs} if req.domain == "NUMERICAL_POLYNOMIAL" else None
    result = _engine.discover(
        workload_fn=fn,
        sample_input=sample,
        workload_name=req.workload_name,
        domain_hint=req.domain,
        max_candidates=req.max_candidates,
        metadata=meta_extra,
    )
    return _sanitize_for_json(result.to_dict())


@router.post("/prove")
def attempt_proof(req: ProveClaimRequest) -> Dict[str, Any]:
    """Attempts symbolic mathematical proof of equivalence using SymPy."""
    cert = _engine.prove_claim(claim_type=req.claim_type, degree=req.degree)
    return _sanitize_for_json(cert.to_dict())


@router.post("/counterexample")
def attack_candidate(req: CounterexampleAttackRequest) -> Dict[str, Any]:
    """Launches adversarial counterexample gauntlet against a candidate."""
    if req.domain in ("SORTING", "BOUNDED_SORTING"):
        ref_fn = lambda arr: np.sort(arr)
        # Deliberately fragile naive counting sort that breaks on large K
        def fragile_sort(arr):
            # Breaks if arr contains elements > 500
            if np.max(arr) > 500:
                raise ValueError("Key out of small range bound!")
            return np.sort(arr)
        cand_fn = fragile_sort
    else:
        ref_fn = lambda x: x * 2.0
        cand_fn = lambda x: x * 2.0

    cx = _engine.attack_callable(
        candidate_fn=cand_fn,
        reference_fn=ref_fn,
        domain=req.domain,
        hypothesis_id=req.hypothesis_id,
    )
    return _sanitize_for_json({
        "counterexample_found": cx is not None,
        "counterexample": cx.to_dict() if cx else None,
        "explanation": cx.explanation if cx else "Candidate survived all adversarial gauntlet stress tests.",
    })


@router.get("/hypotheses")
def list_hypotheses() -> Dict[str, Any]:
    """Returns all research hypotheses tracked in the knowledge graph."""
    nodes = _engine.knowledge_graph.find_nodes_by_type(
        _engine.knowledge_graph.nodes[list(_engine.knowledge_graph.nodes.keys())[0]].node_type.__class__.HYPOTHESIS
    ) if _engine.knowledge_graph.nodes else []
    return _sanitize_for_json({"hypotheses": [n.to_dict() for n in nodes]})


@router.get("/counterexamples")
def list_counterexamples() -> Dict[str, Any]:
    """Returns all discovered adversarial counterexamples."""
    return _sanitize_for_json({"counterexamples": _engine.get_counterexamples()})


@router.get("/proofs")
def list_proofs() -> Dict[str, Any]:
    """Returns all symbolic proof attempts and formal certificates."""
    return _sanitize_for_json({"proofs": _engine.get_proofs()})


@router.get("/rules")
def list_transformation_rules() -> Dict[str, Any]:
    """Returns all discovered rules in the self-improving transformation library."""
    return _sanitize_for_json({"rules": _engine.get_rules()})


@router.get("/knowledge-graph")
def get_knowledge_graph() -> Dict[str, Any]:
    """Returns full serialized Computational Knowledge Graph."""
    return _sanitize_for_json(_engine.get_knowledge_graph_summary())


@router.get("/capability-matrix")
def get_capability_matrix() -> Dict[str, Any]:
    """Returns the verified system capability matrix and maturity level."""
    from hyper.discovery.capability_registry import CapabilityRegistry
    reg = CapabilityRegistry()
    return _sanitize_for_json({
        "system_maturity_level": reg.get_system_maturity_level().value,
        "total_features": len(reg.list_features()),
        "features": [e.model_dump() for e in reg.list_features()],
    })


@router.get("/alphatensor/strassen-2x2x2")
def get_alphatensor_strassen() -> Dict[str, Any]:
    """Evaluates AlphaTensor bilinear decomposition for 2x2x2 matrix multiplication."""
    from hyper.discovery.alphatensor_engine import AlphaTensorEngine
    engine = AlphaTensorEngine()
    problem = engine.create_matrix_multiplication_tensor(2, 2, 2)
    candidate = engine.search_algorithm(problem)
    return _sanitize_for_json(candidate.model_dump())


@router.post("/fairness-check")
def run_fairness_check(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Runs the Benchmark Fairness & Anti-Cheat Engine on provided telemetry."""
    from hyper.discovery.fairness_engine import BenchmarkFairnessEngine
    from hyper.universal.contracts.universal_contract import UniversalContract
    contract = UniversalContract(contract_id="audit", workload_id="sample")
    engine = BenchmarkFairnessEngine()
    report = engine.audit_execution(
        candidate_input=payload.get("input", [1, 2, 3]),
        candidate_output=payload.get("output", [2, 4, 6]),
        reference_input=payload.get("ref_input", [1, 2, 3]),
        reference_output=payload.get("ref_output", [2, 4, 6]),
        contract=contract,
        cache_mode=payload.get("cache_mode", "COLD"),
        measured_time_ns=payload.get("measured_time_ns", 1000),
    )
    return _sanitize_for_json(report.model_dump())


@router.get("/experiments/run-suite")
def run_discovery_suite() -> Dict[str, Any]:
    """Triggers the multi-domain discovery experiment suite."""
    from hyper.discovery.discovery_experiments import DiscoveryExperimentSuite
    suite = DiscoveryExperimentSuite()
    res = suite.run_suite()
    return _sanitize_for_json(res)


@router.get("/capabilities/families")
def list_capability_families() -> Dict[str, Any]:
    """Returns the full 7-family GPU capability taxonomy."""
    return _sanitize_for_json({
        "families": _engine.capability_decomposer.list_all_capabilities()
    })


@router.post("/pathway/generate")
def generate_pathway(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Generates candidate PathwayIRs across mathematical, compiler, memory, runtime, and temporal families."""
    workload = payload.get("workload_name", "Dense_Matrix_Multiplication")
    max_cands = payload.get("max_candidates", 5)
    cands = _engine.generate_pathway_candidates(workload, [1, 2, 3], max_candidates=max_cands)
    return _sanitize_for_json({
        "workload": workload,
        "total_generated": len(cands),
        "candidates": [c.model_dump() for c in cands],
    })


@router.post("/k3/debate")
def run_k3_debate_endpoint(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Triggers a 6-stage multi-agent debate across Kimi K3 research roles."""
    workload = payload.get("workload_name", "Dense_Matrix_Multiplication")
    result = _engine.run_k3_debate(workload)
    return _sanitize_for_json(result.model_dump())


@router.get("/destination-tracker")
def get_destination_tracker() -> Dict[str, Any]:
    """Returns the 100% Destination Tracker metrics."""
    return _sanitize_for_json(_engine.get_destination_tracker_summary())


@router.get("/workloads/controlled-suite")
def run_controlled_suite() -> Dict[str, Any]:
    """Executes the 12 primary controlled workloads and updates destination metrics."""
    reports = _engine.run_controlled_workloads()
    return _sanitize_for_json({
        "total_workloads": len(reports),
        "reports": [r.model_dump() for r in reports],
        "destination_metrics": _engine.get_destination_tracker_summary(),
    })


@router.get("/app-targets")
def list_application_targets() -> Dict[str, Any]:
    """Returns real-world application targets for Blender, Unreal, Unity, WebGPU, Vulkan, PyTorch, etc."""
    from hyper.integrations.app_targets import ApplicationTargetRegistry
    return _sanitize_for_json({
        "targets": ApplicationTargetRegistry.list_targets()
    })


@router.get("/alphadev/catalog")
def get_alphadev_catalog() -> Dict[str, Any]:
    """Returns catalog of discovered branch-free sorting networks and kernels."""
    from hyper.discovery.alphadev_engine import AlphaDevEngine
    dev_engine = AlphaDevEngine()
    return _sanitize_for_json({
        "total_kernels": len(dev_engine.catalog),
        "kernels": [
            {
                "kernel_id": k.kernel_id,
                "name": k.name,
                "input_size": k.input_size,
                "instruction_count": k.instruction_count,
                "is_branch_free": k.is_branch_free,
                "is_verified": k.is_verified,
                "theoretical_comparisons": k.theoretical_comparisons,
                "metadata": k.metadata,
            }
            for k in dev_engine.catalog.values()
        ],
    })


@router.post("/alphadev/benchmark")
def benchmark_alphadev_kernel(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Benchmarks a discovered sorting kernel against canonical sorting."""
    from hyper.discovery.alphadev_engine import AlphaDevEngine
    dev_engine = AlphaDevEngine()
    kernel_key = payload.get("kernel_key", "sort4")
    kernel = dev_engine.catalog.get(kernel_key)
    if not kernel:
        raise HTTPException(status_code=404, detail=f"Kernel {kernel_key} not found")
    
    trials = payload.get("trials", 2000)
    benchmarked = dev_engine.benchmark_sorting_kernel(kernel, trials=trials)
    return _sanitize_for_json({
        "kernel_id": benchmarked.kernel_id,
        "name": benchmarked.name,
        "trials": trials,
        "measured_latency_ns": benchmarked.measured_latency_ns,
        "baseline_latency_ns": benchmarked.baseline_latency_ns,
        "measured_speedup": benchmarked.measured_speedup,
    })


@router.get("/dsl/rules")
def list_dsl_rules() -> Dict[str, Any]:
    """Returns all registered Transformation DSL rules with preconditions and cost models."""
    from hyper.discovery.transformation_dsl import TransformationDSLEngine
    dsl = TransformationDSLEngine()
    return _sanitize_for_json({
        "total_rules": len(dsl.rules),
        "rules": [
            {
                "rule_id": r.rule_id,
                "name": r.name,
                "family": r.family.value,
                "description": r.description,
                "complexity": r.cost_model.complexity_class,
                "estimated_speedup": r.cost_model.estimated_speedup,
                "applicable_domains": list(r.applicable_domains),
            }
            for r in dsl.rules.values()
        ],
    })


@router.get("/research-tracker")
def get_research_tracker_summary() -> Dict[str, Any]:
    """Returns the epistemic validation status of hypotheses H001 through H008."""
    from hyper.discovery.research_tracker import ResearchQuestionTracker
    tracker = ResearchQuestionTracker()
    return _sanitize_for_json(tracker.get_summary())


@router.get("/bypass-engine")
def get_bypass_engine_summary() -> Dict[str, Any]:
    """Returns real-world benchmarks and mathematical proofs across the 5 hardware-bypassing foundations."""
    from hyper.discovery.computational_bypass_engine import ComputationalBypassEngine
    cbe = ComputationalBypassEngine()
    return _sanitize_for_json(cbe.get_summary())



