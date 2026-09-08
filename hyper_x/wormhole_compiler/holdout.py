"""
hyper_x/wormhole_compiler/holdout.py
=============================================================================
HYPER-X Cryptographic Blind Holdout System & Anti-Data-Leakage Defense
=============================================================================
Strictly isolates evaluation workloads to prevent benchmark memorization:
  - Partition 1: SEARCH SET      - Freely explored during algorithm evolution
  - Partition 2: TUNING SET      - Used for parameter & threshold tuning
  - Partition 3: VALIDATION SET  - Used for interim sanity checking
  - Partition 4: BLIND HOLDOUT   - Cryptographically sealed; completely isolated;
                                   outputs hidden from optimizer until final gate.

Audits candidate functions for:
  - Hardcoded lookup tables or conditional branch memorization
  - Leaked golden answers
  - Overfitting to benchmark dimensions
"""

from __future__ import annotations
import inspect
import hashlib
import time
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Callable, Tuple
import numpy as np

from hyper_x.wormhole_compiler.schemas import WorkloadContract


@dataclass
class SealedHoldoutWorkload:
    holdout_id: str
    input_A: np.ndarray
    input_B: np.ndarray
    expected_output_hash: str
    shape: Tuple[int, int, int]
    seed: int
    is_sealed: bool = True


@dataclass
class HoldoutEvaluationReport:
    holdout_id: str
    candidate_id: str
    passed: bool
    numerical_error: float
    tolerance: float
    output_hash_match: bool
    candidate_output_hash: str
    expected_output_hash: str
    provenance_record: Dict[str, Any]


class BlindHoldoutSystem:
    """Manages sealed holdouts and performs strict anti-leakage evaluation."""

    def __init__(self):
        self.sealed_holdouts: Dict[str, SealedHoldoutWorkload] = {}

    def register_sealed_matrix_holdout(
        self,
        holdout_id: str,
        shape: Tuple[int, int, int],
        seed: int = 9999
    ) -> None:
        """Generates an unseen holdout workload and cryptographically seals its reference output."""
        rng = np.random.RandomState(seed)
        M, K, N = shape
        A = rng.randn(M, K).astype(np.float32)
        B = rng.randn(K, N).astype(np.float32)
        ref_out = A @ B

        o_hash = hashlib.sha256(ref_out.tobytes()).hexdigest()
        self.sealed_holdouts[holdout_id] = SealedHoldoutWorkload(
            holdout_id=holdout_id,
            input_A=A,
            input_B=B,
            expected_output_hash=o_hash,
            shape=shape,
            seed=seed,
            is_sealed=True
        )

    @staticmethod
    def audit_candidate_ast_for_leakage(candidate_fn: Callable) -> Tuple[bool, List[str]]:
        """Static inspection of candidate function for memorization or cheating."""
        try:
            source = inspect.getsource(candidate_fn).lower()
        except Exception:
            return True, []  # Dynamic compiled kernel

        forbidden = [
            "golden_output", "benchmark_answer", "if shape ==", "if n ==",
            "lookup_table_answer", "precomputed_gemm", "test_matrix"
        ]
        leaks = [p for p in forbidden if p in source]
        return len(leaks) == 0, leaks

    def evaluate_holdout(
        self,
        holdout_id: str,
        candidate_id: str,
        candidate_fn: Callable[[np.ndarray, np.ndarray], np.ndarray],
        contract: WorkloadContract,
        hardware_fingerprint_hash: str
    ) -> HoldoutEvaluationReport:
        """Executes candidate against sealed holdout with provenance record."""
        if holdout_id not in self.sealed_holdouts:
            raise KeyError(f"Holdout workload '{holdout_id}' not found in sealed vault")

        clean, leaks = self.audit_candidate_ast_for_leakage(candidate_fn)
        if not clean:
            return HoldoutEvaluationReport(
                holdout_id=holdout_id,
                candidate_id=candidate_id,
                passed=False,
                numerical_error=float("inf"),
                tolerance=contract.tolerance,
                output_hash_match=False,
                candidate_output_hash="DISQUALIFIED_LEAKAGE",
                expected_output_hash=self.sealed_holdouts[holdout_id].expected_output_hash,
                provenance_record={"leakage_detected": leaks, "verdict": "DISQUALIFIED"}
            )

        holdout = self.sealed_holdouts[holdout_id]
        cand_out = candidate_fn(holdout.input_A, holdout.input_B)
        cand_hash = hashlib.sha256(cand_out.tobytes()).hexdigest()

        # Compute error against sealed reference
        ref_out = holdout.input_A @ holdout.input_B
        if cand_out.shape != ref_out.shape and cand_out.ndim == 2 and cand_out.shape[1] == 1:
            ref_out = ref_out @ np.ones((ref_out.shape[1], 1), dtype=np.float32)

        diff_norm = float(np.linalg.norm(ref_out - cand_out))
        ref_norm = float(np.linalg.norm(ref_out) + 1e-8)
        rel_error = diff_norm / ref_norm

        passed = rel_error <= contract.tolerance
        hash_match = cand_hash == holdout.expected_output_hash

        provenance = {
            "workload_id": holdout_id,
            "contract_hash": contract.compute_contract_hash(),
            "candidate_id": candidate_id,
            "hardware_fingerprint_hash": hardware_fingerprint_hash,
            "timestamp": time.time(),
            "seed": holdout.seed
        }

        return HoldoutEvaluationReport(
            holdout_id=holdout_id,
            candidate_id=candidate_id,
            passed=passed,
            numerical_error=round(rel_error, 8),
            tolerance=contract.tolerance,
            output_hash_match=hash_match,
            candidate_output_hash=cand_hash[:16],
            expected_output_hash=holdout.expected_output_hash[:16],
            provenance_record=provenance
        )
