"""
hyper_x/wormhole_compiler/learned_shortcuts.py
=============================================================================
HYPER-X Learned Shortcuts & Speculative Predictors with Safe Verification
=============================================================================
Allows learned surrogates / heuristic neural models to propose shortcuts, but
STRICTLY enforces that AI prediction alone is NOT proof of correctness:

  Predictor
      ↓
  Candidate Shortcut + Confidence
      ↓
  Applicability Detector
      ↓
  Independent Verifier (Freivalds / Contract Bound)
      ↓
  Accept (Verified Output)  OR  Reject (Safe Fallback + Failure Record)
"""

from __future__ import annotations
import time
from typing import Dict, Any, Tuple, Optional, Callable
import numpy as np

from hyper_x.wormhole_compiler.schemas import WorkloadContract


class LearnedShortcutEngine:
    """Proposes shortcuts using feature heuristics with strictly enforced verification."""

    def __init__(self):
        # Learned confidence weights mapping feature signals to shortcuts
        self.policy_weights: Dict[str, float] = {
            "low_rank_svd": 1.0,
            "sparse_skip": 1.0,
            "temporal_delta": 1.2,
            "spectral_fft": 0.8
        }
        self.rejected_proposals_count: int = 0
        self.accepted_proposals_count: int = 0

    def extract_workload_features(self, A: np.ndarray) -> Dict[str, float]:
        """Extracts lightweight mathematical features from the input tensor."""
        sample_size = min(64, min(A.shape))
        sample = A[:sample_size, :sample_size]

        # 1. Sparsity
        sparsity = float(np.mean(np.abs(sample) < 1e-4))

        # 2. Singular value decay
        s = np.linalg.svd(sample, compute_uv=False)
        energy_cdf = np.cumsum(s**2) / np.sum(s**2)
        r95 = int(np.searchsorted(energy_cdf, 0.95)) + 1
        rank_ratio = r95 / max(1, sample_size)

        # 3. Dynamic range / condition number estimate
        cond_est = float(s[0] / max(1e-8, s[-1]))

        return {
            "sparsity": sparsity,
            "rank_ratio": rank_ratio,
            "condition_number": cond_est,
            "sample_dim": float(sample_size)
        }

    def propose_and_verify(
        self,
        A: np.ndarray,
        B: np.ndarray,
        contract: WorkloadContract,
        candidate_fn: Callable[[], np.ndarray],
        verifier_fn: Callable[[np.ndarray], Tuple[bool, float]]
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Executes proposal with strict independent verification and safe fallback.
        """
        feats = self.extract_workload_features(A)
        t0 = time.perf_counter()

        # Applicability check
        confidence = 0.5
        if feats["rank_ratio"] < 0.4:
            confidence += 0.3 * self.policy_weights.get("low_rank_svd", 1.0)
        if feats["sparsity"] > 0.4:
            confidence += 0.3 * self.policy_weights.get("sparse_skip", 1.0)

        # Execute speculative candidate
        candidate_out = candidate_fn()
        verified, error_metric = verifier_fn(candidate_out)

        if verified and error_metric <= contract.tolerance:
            # Accepted!
            self.accepted_proposals_count += 1
            elapsed_ms = (time.perf_counter() - t0) * 1000.0
            return candidate_out, {
                "shortcut_accepted": True,
                "verified": True,
                "confidence_score": round(confidence, 3),
                "error_metric": round(error_metric, 6),
                "fallback_used": False,
                "latency_ms": round(elapsed_ms, 3)
            }
        else:
            # Rejected! Revert to safe reference execution
            self.rejected_proposals_count += 1
            # Penalize policy weight
            self.policy_weights["low_rank_svd"] = max(0.2, self.policy_weights.get("low_rank_svd", 1.0) * 0.85)

            ref_out = A @ B
            elapsed_ms = (time.perf_counter() - t0) * 1000.0
            return ref_out, {
                "shortcut_accepted": False,
                "verified": False,
                "rejection_reason": f"Verification error {error_metric:.2e} exceeded tolerance {contract.tolerance:.2e}",
                "confidence_score": round(confidence, 3),
                "error_metric": round(error_metric, 6),
                "fallback_used": True,
                "latency_ms": round(elapsed_ms, 3)
            }
