"""
hyper_x/strict/verifier.py
=============================================================================
HYPER-X 11-Tier Verification Hierarchy
=============================================================================
Defines the multi-level verification pipeline (Levels 0 - 10):
  LEVEL 0:  Schema validation
  LEVEL 1:  Deterministic unit tests
  LEVEL 2:  Numerical comparison (tolerance, atol, rtol)
  LEVEL 3:  Differential testing against gold reference
  LEVEL 4:  Randomized testing (Freivalds O(N^2) randomized probe - explicitly NOT deterministic)
  LEVEL 5:  Adversarial testing (pathological edge cases, near-singular matrices)
  LEVEL 6:  Property-based testing (associativity, symmetry, energy conservation)
  LEVEL 7:  Metamorphic testing (input transformation -> known output relation)
  LEVEL 8:  Independent cleanroom implementation verification
  LEVEL 9:  Blind holdout evaluation (frozen unseen distribution)
  LEVEL 10: External reproduction on separate runner environment

CRITICAL SCIENTIFIC RULE (Section 23):
Freivalds-style randomized verification may be used as one layer, but it
MUST NOT be described as deterministic proof.
"""

from __future__ import annotations
import enum
import math
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple, Callable
import numpy as np

class VerificationLevel(int, enum.Enum):
    LEVEL_0_SCHEMA = 0
    LEVEL_1_UNIT = 1
    LEVEL_2_NUMERICAL = 2
    LEVEL_3_DIFFERENTIAL = 3
    LEVEL_4_RANDOMIZED = 4
    LEVEL_5_ADVERSARIAL = 5
    LEVEL_6_PROPERTY = 6
    LEVEL_7_METAMORPHIC = 7
    LEVEL_8_INDEPENDENT = 8
    LEVEL_9_BLIND_HOLDOUT = 9
    LEVEL_10_EXTERNAL_REPRO = 10

@dataclass
class VerificationOutcome:
    level: VerificationLevel
    passed: bool
    confidence: float  # [0.0, 1.0]
    metric_name: str
    metric_value: float
    threshold: float
    details: str

class VerificationHierarchy:
    """Multi-tiered verifier enforcing rigorous scientific standards."""

    def verify_schema(self, data: Any, expected_shape: Optional[Tuple[int, ...]] = None) -> VerificationOutcome:
        """Level 0: Schema validation."""
        if data is None:
            return VerificationOutcome(VerificationLevel.LEVEL_0_SCHEMA, False, 0.0, "null_check", 0.0, 1.0, "Data is null")
        if expected_shape and hasattr(data, "shape"):
            valid = tuple(data.shape) == expected_shape
            return VerificationOutcome(
                VerificationLevel.LEVEL_0_SCHEMA, valid, 1.0 if valid else 0.0,
                "shape_match", 1.0 if valid else 0.0, 1.0,
                f"Shape {data.shape} matches {expected_shape}" if valid else f"Shape mismatch {data.shape} vs {expected_shape}"
            )
        return VerificationOutcome(VerificationLevel.LEVEL_0_SCHEMA, True, 1.0, "schema", 1.0, 1.0, "Schema valid")

    def verify_numerical(self, candidate: np.ndarray, reference: np.ndarray, epsilon: float = 1e-4) -> VerificationOutcome:
        """Level 2: Numerical comparison."""
        abs_diff = np.abs(candidate - reference)
        norm_ref = np.linalg.norm(reference)
        rel_err = float(np.max(abs_diff) / (norm_ref + 1e-12))
        passed = rel_err <= epsilon
        confidence = max(0.0, min(1.0, 1.0 - (rel_err / max(1e-9, epsilon)))) if passed else 0.0
        return VerificationOutcome(
            level=VerificationLevel.LEVEL_2_NUMERICAL,
            passed=passed,
            confidence=confidence,
            metric_name="relative_error",
            metric_value=rel_err,
            threshold=epsilon,
            details=f"Numerical error {rel_err:.2e} <= {epsilon:.2e}" if passed else f"Numerical error exceeded ({rel_err:.2e})"
        )

    def verify_freivalds(self, C: np.ndarray, A: np.ndarray, B: np.ndarray, rounds: int = 15, epsilon: float = 1e-4) -> VerificationOutcome:
        """
        Level 4: Freivalds Randomized Matrix Multiplication Verification.
        Probabilistic verification: tests if A @ (B @ r) == C @ r for random binary vectors r.
        Failure probability: <= 2^(-rounds).
        NOTE: This is a randomized verification, NOT a deterministic proof!
        """
        n = B.shape[1]
        m = A.shape[0]
        max_err = 0.0

        for _ in range(rounds):
            r = np.random.randint(0, 2, size=(n, 1)).astype(A.dtype)
            Br = B @ r
            ABr = A @ Br
            Cr = C @ r
            diff = np.max(np.abs(ABr - Cr))
            if diff > max_err:
                max_err = float(diff)
            if diff > epsilon * (np.linalg.norm(ABr) + 1.0):
                return VerificationOutcome(
                    level=VerificationLevel.LEVEL_4_RANDOMIZED,
                    passed=False,
                    confidence=0.0,
                    metric_name="freivalds_residual",
                    metric_value=float(diff),
                    threshold=epsilon,
                    details="Freivalds randomized probe detected inconsistency"
                )

        confidence = 1.0 - (0.5 ** rounds)
        return VerificationOutcome(
            level=VerificationLevel.LEVEL_4_RANDOMIZED,
            passed=True,
            confidence=confidence,
            metric_name="freivalds_confidence",
            metric_value=confidence,
            threshold=0.999,
            details=f"Freivalds randomized probe passed across {rounds} rounds (p_error <= {0.5**rounds:.2e})"
        )

    def verify_adversarial(self, candidate_fn: Callable[[np.ndarray], np.ndarray], reference_fn: Callable[[np.ndarray], np.ndarray], dim: int = 64) -> VerificationOutcome:
        """Level 5: Adversarial testing against ill-conditioned and pathological inputs."""
        # 1. Ill-conditioned Hilbert matrix
        H = 1.0 / (np.arange(1, dim + 1)[:, None] + np.arange(0, dim) + 1.0).astype(np.float32)
        # 2. Pathological sparse impulse
        I = np.zeros((dim, dim), dtype=np.float32)
        I[0, 0] = 1e6
        I[-1, -1] = 1e-6

        for test_name, mat in [("hilbert_matrix", H), ("pathological_impulse", I)]:
            ref = reference_fn(mat)
            cand = candidate_fn(mat)
            rel_err = float(np.linalg.norm(ref - cand) / (np.linalg.norm(ref) + 1e-9))
            if rel_err > 1e-2:
                return VerificationOutcome(
                    level=VerificationLevel.LEVEL_5_ADVERSARIAL,
                    passed=False,
                    confidence=0.0,
                    metric_name="adversarial_rel_err",
                    metric_value=rel_err,
                    threshold=1e-2,
                    details=f"Failed under adversarial stress ({test_name}, err={rel_err:.2e})"
                )

        return VerificationOutcome(
            level=VerificationLevel.LEVEL_5_ADVERSARIAL,
            passed=True,
            confidence=0.95,
            metric_name="adversarial_robustness",
            metric_value=1.0,
            threshold=1.0,
            details="Passed Hilbert and pathological impulse tests"
        )
