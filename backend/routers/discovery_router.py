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
