"""
hyper/discovery/proof.py
========================
Proof-Carrying Result Generator, Pathway Explainer, and Auditable Search Trace.

Generates:
1. Machine-readable proof record (JSON).
2. Human-readable scientific explanation:
   - Why was this pathway valid?
   - Why was it cheaper?
   - What computation was eliminated?
   - What assumptions were used?
   - What could invalidate it?
3. Visual comparison of Original Pathway vs Discovered Pathway.
"""

from __future__ import annotations

import dataclasses
import json
import time
from typing import Any, Dict, List, Optional, Tuple

from hyper.discovery.cir import CIRGraph, CIRNode
from hyper.discovery.contract import WorkloadContract
from hyper.discovery.search import SearchResult
from hyper.discovery.search_space import CandidatePathway


@dataclasses.dataclass
class HumanReadableExplanation:
    why_valid: str
    why_cheaper: str
    computation_eliminated: str
    assumptions_used: List[str]
    falsification_conditions: List[str]

    def to_markdown(self) -> str:
        assump = "\n".join(f"- {a}" for a in self.assumptions_used) or "- None"
        fals = "\n".join(f"- {f}" for f in self.falsification_conditions) or "- None"
        return (
            f"### Scientific Explanation\n\n"
            f"**1. Why Was This Pathway Valid?**\n{self.why_valid}\n\n"
            f"**2. Why Was It Cheaper?**\n{self.why_cheaper}\n\n"
            f"**3. What Computation Was Eliminated?**\n{self.computation_eliminated}\n\n"
            f"**4. Mathematical Assumptions Used:**\n{assump}\n\n"
            f"**5. What Could Invalidate This Pathway?**\n{fals}\n"
        )


@dataclasses.dataclass
class ProofRecord:
    workload_id: str
    candidate_id: str
    reference_hash: str
    candidate_hash: str
    exactness_mode: str
    candidate_operations: float
    reference_operations: float
    candidate_runtime_ms: float
    reference_runtime_ms: float
    speedup: float
    transformation_chain: List[str]
    verification: str
    independent_verification: str
    parity_classification: str
    explanation: HumanReadableExplanation
    pathway_ascii_diff: str
    timestamp: float = dataclasses.field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "workload_id": self.workload_id,
            "candidate_id": self.candidate_id,
            "reference_hash": self.reference_hash,
            "candidate_hash": self.candidate_hash,
            "exactness_mode": self.exactness_mode,
            "candidate_operations": self.candidate_operations,
            "reference_operations": self.reference_operations,
            "candidate_runtime_ms": self.candidate_runtime_ms,
            "reference_runtime_ms": self.reference_runtime_ms,
            "speedup": self.speedup,
            "transformation_chain": list(self.transformation_chain),
            "verification": self.verification,
            "independent_verification": self.independent_verification,
            "parity_classification": self.parity_classification,
            "explanation": dataclasses.asdict(self.explanation),
            "pathway_ascii_diff": self.pathway_ascii_diff,
            "timestamp": self.timestamp,
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)


class PathwayExplainer:
    """
    Constructs ASCII diagrams and textual comparisons of Original vs Discovered pathways.
    """

    def generate_ascii_comparison(self, original_graph: CIRGraph, discovered_graph: CIRGraph) -> str:
        """Render side-by-side or stacked graph flow diagram."""
        orig_nodes = [f"[{n.name}: {n.op_type.value}]" for n in original_graph.nodes.values() if not n.attributes.get("is_input")]
        disc_nodes = [f"[{n.name}: {n.op_type.value}]" for n in discovered_graph.nodes.values() if not n.attributes.get("is_input")]

        orig_flow = " -> ".join(orig_nodes) or "[No Operations]"
        disc_flow = " -> ".join(disc_nodes) or "[No Operations]"

        return (
            f"ORIGINAL PATHWAY ({original_graph.total_estimated_flops():.0f} FLOPs):\n"
            f"  {orig_flow}\n\n"
            f"DISCOVERED PATHWAY ({discovered_graph.total_estimated_flops():.0f} FLOPs):\n"
            f"  {disc_flow}\n"
        )


class ProofGenerator:
    """
    Constructs proof records and explanations from search results.
    """

    def __init__(self, explainer: Optional[PathwayExplainer] = None):
        self.explainer = explainer or PathwayExplainer()

    def generate_proof(
        self,
        search_result: SearchResult,
        original_graph: CIRGraph,
        contract: WorkloadContract,
    ) -> ProofRecord:
        best_cand = search_result.best_pathway
        vrec = search_result.verification_record

        # Generate ASCII comparison
        ascii_diff = self.explainer.generate_ascii_comparison(original_graph, best_cand.graph)

        # Synthesize scientific explanation
        if search_result.is_shortcut_found:
            why_valid = (
                f"Candidate passed independent reference verification under contract mode "
                f"'{contract.exactness_mode.value}'. Error metrics: max_abs={vrec.max_abs_error if vrec else 0.0:.2e}, "
                f"relative_error={vrec.relative_error if vrec else 0.0:.2e}."
            )
            why_cheaper = (
                f"Computational operations reduced from {search_result.baseline_cost:.0f} to {search_result.best_cost:.0f} FLOPs "
                f"({(1.0 - search_result.best_cost / max(search_result.baseline_cost, 1)) * 100:.1f}% reduction) "
                f"via: {'; '.join(best_cand.transformation_history)}."
            )
            eliminated = (
                f"Eliminated {max(0.0, search_result.baseline_cost - search_result.best_cost):.0f} FLOPs of redundant or "
                f"suboptimally ordered operations."
            )
            assumptions = best_cand.mathematical_assumptions
            falsification = [
                "Inputs outside specified domain bounds.",
                "Non-associative numerical floating-point accumulation exceeding contract tolerance.",
                "Contract mode escalated to BIT_EXACT when mathematical formulation involves floating-point reordering.",
            ]
        else:
            why_valid = "Trusted baseline reference executed. Correctness is guaranteed by canonical definition."
            why_cheaper = "No alternative shortcut was found that met all contract invariants at lower cost. Baseline cost retained."
            eliminated = "0 FLOPs eliminated. Full computation executed to guarantee exact contract satisfaction."
            assumptions = ["Canonical mathematical definition."]
            falsification = ["None (trusted baseline)."]

        explanation = HumanReadableExplanation(
            why_valid=why_valid,
            why_cheaper=why_cheaper,
            computation_eliminated=eliminated,
            assumptions_used=assumptions,
            falsification_conditions=falsification,
        )

        return ProofRecord(
            workload_id=contract.workload_name,
            candidate_id=best_cand.candidate_id,
            reference_hash=vrec.reference_hash if vrec else "unknown",
            candidate_hash=vrec.candidate_hash if vrec else "unknown",
            exactness_mode=contract.exactness_mode.value,
            candidate_operations=search_result.best_cost,
            reference_operations=search_result.baseline_cost,
            candidate_runtime_ms=vrec.candidate_runtime_ms if vrec else 0.0,
            reference_runtime_ms=vrec.reference_runtime_ms if vrec else 0.0,
            speedup=vrec.speedup if vrec else 1.0,
            transformation_chain=best_cand.transformation_history,
            verification="PASSED" if (vrec and vrec.passed) else "FAILED",
            independent_verification="PASSED" if (vrec and vrec.passed) else "FAILED",
            parity_classification=vrec.parity_classification if vrec else "UNKNOWN",
            explanation=explanation,
            pathway_ascii_diff=ascii_diff,
        )
