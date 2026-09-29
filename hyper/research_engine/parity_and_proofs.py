"""
hyper/research_engine/parity_and_proofs.py
==========================================
Proof-Carrying Computation, Pathway Visualization, Failure Explanation,
Universality Matrix, and the 100% Destination Gate.

Implements Sections 28, 29, 30, 31, 32, and 33:
- Cryptographic proof.json generation
- Structural pathway visualization (Original vs. Discovered)
- Multi-category Failure Explanation Engine
- Seven-dimension Parity Matrix
- Strict PARITY_100_GATE
"""

from __future__ import annotations
import dataclasses
import hashlib
import json
import os
import platform
import time
from typing import Any, Dict, List, Optional
import numpy as np

from hyper.research_engine.contracts import ProblemContract
from hyper.research_engine.exactness import ExactnessMode
from hyper.research_engine.counterexample_verifier import EquivalenceProof
from hyper.research_engine.search_and_cost import WorkloadCostProfile
from hyper.research_engine.solution_space_compiler import CandidatePathway


class ProofCarryingComputation:
    """Generates immutable, cryptographically verifiable proof.json artifacts."""

    @classmethod
    def generate_proof(
        cls,
        contract: ProblemContract,
        candidate: CandidatePathway,
        cost_profile: WorkloadCostProfile,
        equivalence_proof: EquivalenceProof,
        inputs: Dict[str, Any],
        reference_output: Any,
        candidate_output: Any,
    ) -> Dict[str, Any]:
        
        # Calculate cryptographic hashes
        def hash_tensor(t: Any) -> str:
            if isinstance(t, np.ndarray):
                return hashlib.sha256(t.tobytes()).hexdigest()
            return hashlib.sha256(str(t).encode()).hexdigest()

        input_hashes = {k: hash_tensor(v) for k, v in inputs.items()}
        ref_out_hash = hash_tensor(reference_output)
        cand_out_hash = hash_tensor(candidate_output)

        proof_doc = {
            "proof_id": f"proof_{hashlib.sha256(f'{contract.workload_id}_{candidate.candidate_id}_{time.time()}'.encode()).hexdigest()[:16]}",
            "problem_id": contract.workload_id,
            "contract_hash": contract.get_contract_hash(),
            "original_cir_hash": candidate.cir_hash,
            "candidate_id": candidate.candidate_id,
            "transformation_chain": candidate.transformation_history,
            "assumptions": candidate.assumptions,
            "input_hashes": input_hashes,
            "reference_output_hash": ref_out_hash,
            "candidate_output_hash": cand_out_hash,
            "exactness_mode": candidate.exactness_mode.value,
            "verification_status": "VERIFIED" if equivalence_proof.is_verified else "FAILED",
            "verification_method": equivalence_proof.verification_method,
            "max_absolute_error": equivalence_proof.max_error,
            "counterexamples_evaluated": equivalence_proof.tests_evaluated,
            "counterexamples_failed": len(equivalence_proof.counterexamples_found),
            "performance": {
                "execution_latency_ms": cost_profile.execution_time_ms,
                "discovery_latency_ms": cost_profile.discovery_time_ms,
                "verification_latency_ms": cost_profile.verification_time_ms,
                "total_first_run_ms": cost_profile.total_first_run_ms,
                "flops": cost_profile.flops,
                "memory_traffic_bytes": cost_profile.total_memory_traffic_bytes,
            },
            "environment": {
                "platform": platform.platform(),
                "processor": platform.processor(),
                "python_version": platform.python_version(),
            },
            "timestamp": time.time(),
        }

        # Save to experiment folder
        exp_dir = f"experiments/{proof_doc['proof_id']}"
        os.makedirs(exp_dir, exist_ok=True)
        with open(f"{exp_dir}/proof.json", "w", encoding="utf-8") as f:
            json.dump(proof_doc, f, indent=2)

        return proof_doc


class PathwayVisualizer:
    """Generates comparative visualizations showing how a discovered pathway transformed the computation."""

    @classmethod
    def format_pathway_comparison(cls, candidate: CandidatePathway, contract: ProblemContract) -> str:
        lines = [
            "=" * 70,
            f" COMPUTATIONAL PATHWAY COMPARISON: {contract.workload_id}",
            "=" * 70,
            "ORIGINAL CANONICAL PATHWAY:",
            "  [Input Tensors] -> Standard Full Materialization -> [Output]",
            "",
            "DISCOVERED TRANSFORMED PATHWAY:",
            f"  Candidate ID: {candidate.candidate_id}",
            f"  Transformation Chain: {' -> '.join(candidate.transformation_history)}",
            "",
            "OPTIMIZATION ANALYSIS:",
            f"  - Flops Scale:      {candidate.estimated_cost.get('flops', 1.0)*100:.1f}% of baseline",
            f"  - Memory Traffic:   {candidate.estimated_cost.get('memory_traffic', 1.0)*100:.1f}% of baseline",
            f"  - Declared Mode:    {candidate.exactness_mode.value}",
            "",
            "WHY IS THIS EXACT?",
            f"  {cls._generate_exactness_rationale(candidate)}",
            "=" * 70,
        ]
        return "\n".join(lines)

    @classmethod
    def _generate_exactness_rationale(cls, candidate: CandidatePathway) -> str:
        history_str = " ".join(candidate.transformation_history)
        if "STRASSEN" in history_str:
            return "Strassen bilinear decomposition is an exact polynomial identity in the ring of matrices; residual ||T - T_cand|| == 0."
        elif "HORNERS" in history_str:
            return "Horner's rule is an exact algebraic factoring of polynomial expressions preserving exact mathematical equality."
        elif "WINOGRAD" in history_str:
            return "Winograd minimal filtering operates via exact Chinese Remainder Theorem polynomial factorization."
        elif "TILING" in history_str:
            return "Tiling reorders summation indices over associative and commutative linear operations; mathematically invariant."
        elif "LOW_RANK" in history_str:
            return "Low-rank truncation maintains contract accuracy by bounding singular value tails within user-declared tolerance epsilon."
        return "Transformation preserves algebraic input-output contract."


class FailureExplanationEngine:
    """Taxonomy of failure modes when a candidate or experiment does not achieve 100% parity."""

    TAXONOMY = {
        "MEMORY_BOUND": "Workload arithmetic intensity is below laptop DDR RAM saturation point; hardware memory bandwidth is physical ceiling.",
        "COMPUTE_BOUND": "Algorithmic lower bound precludes further operation elimination without loss of contract exactness.",
        "VERIFICATION_FAILURE": "Candidate diverged from independent canonical reference on one or more adversarial counterexamples.",
        "SEARCH_BUDGET_EXHAUSTED": "Search escalation ceiling reached before discovering a contract-preserving transformation.",
        "NUMERICAL_INSTABILITY": "Accumulated floating-point rounding or ill-conditioned input exceeded tolerance threshold.",
        "IRREDUCIBLE_ENTROPY": "Workload is cryptographically random or high-entropy, precluding state bypass.",
    }

    @classmethod
    def explain_failure(cls, failure_category: str, details: str = "") -> Dict[str, str]:
        description = cls.TAXONOMY.get(failure_category, "Unclassified computational limitation.")
        return {
            "failure_category": failure_category,
            "explanation": description,
            "details": details,
        }


@dataclasses.dataclass
class ParityMatrix:
    """The seven distinct, un-collapsed parity measurements."""
    hardware_parity: float = 0.0          # Physically disjoint (Laptop CPU/iGPU vs Discrete GPU)
    exact_compute_parity: float = 0.0     # Percentage of workload domain with bit-exact/symbolic parity
    contract_parity: float = 0.0          # Percentage meeting full user contract
    performance_parity: float = 0.0       # Empirical speedup ratio vs. target
    energy_parity: float = 0.0            # Energy ratio per workload
    memory_parity: float = 0.0            # Memory footprint & traffic ratio
    throughput_parity: float = 0.0        # Continuous throughput ratio

    def to_dict(self) -> Dict[str, Any]:
        return {
            "hardware_parity_pct": self.hardware_parity,
            "exact_compute_parity_pct": self.exact_compute_parity,
            "contract_parity_pct": self.contract_parity,
            "performance_parity_pct": self.performance_parity,
            "energy_parity_pct": self.energy_parity,
            "memory_parity_pct": self.memory_parity,
            "throughput_parity_pct": self.throughput_parity,
            "is_100_percent_exact_compute": self.exact_compute_parity == 100.0,
        }


class Parity100Gate:
    """
    100% Destination Gate: Evaluates whether full research parity has been earned.
    Passes ONLY when all criteria are strictly satisfied without fabrication.
    """

    @classmethod
    def evaluate(
        cls,
        parity_matrix: ParityMatrix,
        all_workloads_verified: bool,
        blind_holdout_passed: bool,
        anti_cheat_clean: bool,
        resource_constraints_satisfied: bool,
    ) -> Tuple[bool, List[str]]:
        reasons = []

        if not all_workloads_verified:
            reasons.append("Not all declared workloads passed independent dual-path verification")
        if not blind_holdout_passed:
            reasons.append("Blind holdout evaluation failed or suffered leakage")
        if not anti_cheat_clean:
            reasons.append("Anti-hardcoding static/runtime audit detected suspicious patterns")
        if not resource_constraints_satisfied:
            reasons.append("Candidate violated local hardware/memory bounds")
        if parity_matrix.exact_compute_parity < 100.0:
            reasons.append(f"Exact-compute parity is {parity_matrix.exact_compute_parity:.1f}% (target: 100.0%)")

        gate_passed = len(reasons) == 0
        return gate_passed, reasons
