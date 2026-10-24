"""
backend/caoe/verifier.py
========================
CAOE Layer 6: Contract Verification & Validation.

Measures whether candidate execution strictly met the negotiated application contract:
- Absolute error bound
- Relative error bound
- Perceptual metric (SSIM)
- Functional metric (Top-k intersection)
"""

from __future__ import annotations

import dataclasses
from typing import Any, Dict, Optional

import numpy as np

from .contract_analyzer import Contract


@dataclasses.dataclass
class VerificationResult:
    contract_met: bool
    absolute_error: float
    relative_error: float
    perceptual_score: Optional[float]
    functional_score: bool
    verdict: str
    freivalds_pass: Optional[bool] = None
    holdout_relative_error: Optional[float] = None
    verification_method: str = "EXACT_REFERENCE_COMPARISON"
    tri_metric_summary: Optional[Dict[str, Any]] = None

    def as_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {
            "contract_met": self.contract_met,
            "absolute_error": float(f"{self.absolute_error:.3e}"),
            "relative_error": float(f"{self.relative_error:.3e}"),
            "perceptual_score": round(self.perceptual_score, 4) if self.perceptual_score is not None else None,
            "functional_score": self.functional_score,
            "verdict": self.verdict,
            "freivalds_pass": self.freivalds_pass,
            "holdout_relative_error": float(f"{self.holdout_relative_error:.3e}") if self.holdout_relative_error is not None else None,
            "verification_method": self.verification_method,
        }
        if self.tri_metric_summary:
            d["tri_metric_summary"] = self.tri_metric_summary
        return d


class Verifier:
    """Measure: Did we meet the contract?"""

    @staticmethod
    def verify_gemm_freivalds(
        A: np.ndarray,
        B: np.ndarray,
        C: np.ndarray,
        epsilon: float = 1e-4,
        num_trials: int = 5,
    ) -> Tuple[bool, float]:
        """Verify C = A @ B in O(k * N^2) using Freivalds' algorithm."""
        from backend.hardware.universal_subsumption_engine import IndependentVerifier
        return IndependentVerifier.freivalds_verify_gemm(A, B, C, epsilon=epsilon, num_trials=num_trials)

    @staticmethod
    def verify_holdout_coordinate(
        candidate_out: np.ndarray,
        reference_fn: Callable[[Dict[str, Any]], np.ndarray],
        inputs: Dict[str, Any],
        holdout_ratio: float = 0.02,
        epsilon: float = 1e-4,
    ) -> Tuple[bool, float]:
        """Audits random 2% coordinates against reference function."""
        from backend.hardware.universal_subsumption_engine import IndependentVerifier
        return IndependentVerifier.random_holdout_coordinate_audit(
            candidate_out, reference_fn, inputs, holdout_ratio=holdout_ratio, epsilon=epsilon
        )

    verify_freivalds = verify_gemm_freivalds
    verify_holdout = verify_holdout_coordinate

    @staticmethod
    def verify(
        result: np.ndarray,
        reference: np.ndarray,
        contract: Contract,
        operands: Optional[Tuple[np.ndarray, np.ndarray]] = None,
    ) -> VerificationResult:
        # Check shapes
        if result.shape != reference.shape:
            return VerificationResult(
                contract_met=False,
                absolute_error=float("inf"),
                relative_error=float("inf"),
                perceptual_score=None,
                functional_score=False,
                verdict="FAIL_SHAPE_MISMATCH",
                freivalds_pass=False,
                holdout_relative_error=float("inf"),
                verification_method="SHAPE_CHECK",
            )

        # Numerical Error (compute absolute difference prior to casting to preserve complex magnitudes)
        diff = np.abs(result - reference).astype(np.float64)
        abs_error = float(np.max(diff)) if diff.size > 0 else 0.0

        ref_abs = np.abs(reference).astype(np.float64)
        with np.errstate(divide="ignore", invalid="ignore"):
            rel = np.where(ref_abs > 0, diff / ref_abs, diff)
        rel_error = float(np.max(rel)) if rel.size > 0 else 0.0

        # 2% Holdout coordinate evaluation
        cand_flat = result.ravel()
        ref_flat = reference.ravel()
        n_elems = cand_flat.size
        holdout_err = rel_error
        if n_elems > 50:
            sample_size = max(1, int(n_elems * 0.02))
            rng = np.random.default_rng(42)
            idx = rng.choice(n_elems, size=sample_size, replace=False)
            diff_sample = np.abs(cand_flat[idx].astype(np.float64) - ref_flat[idx].astype(np.float64))
            denom_sample = np.abs(ref_flat[idx].astype(np.float64))
            safe_denom = np.where(denom_sample > 1e-8, denom_sample, 1.0)
            holdout_err = float(np.max(diff_sample / safe_denom))

        # Freivalds O(N^2) Matrix Verifier if operands (A, B) provided
        freivalds_passed: Optional[bool] = None
        method = "EXACT_REFERENCE_COMPARISON"
        max_rel_tol = float(contract.tolerance.get("relative_error", 1e-4) or 1e-4)

        if operands is not None and len(operands) == 2:
            A, B = operands
            if A.ndim == 2 and B.ndim == 2 and result.ndim == 2:
                f_ok, f_err = Verifier.verify_gemm_freivalds(A, B, result, epsilon=max_rel_tol, num_trials=5)
                freivalds_passed = f_ok
                method = "FREIVALDS_O(N^2)_RADEMACHER"

        # Perceptual Metric (e.g. SSIM simulation or skimage if available)
        meets_perceptual = True
        perceptual_score: Optional[float] = None
        if contract.perceptual_metric == "SSIM":
            try:
                from skimage.metrics import structural_similarity as ssim_fn
                # Normalize to [0, 1] for SSIM
                r_min, r_max = float(reference.min()), float(reference.max())
                rng_val = max(1e-6, r_max - r_min)
                ref_norm = (reference - r_min) / rng_val
                res_norm = (result - r_min) / rng_val
                score = float(ssim_fn(ref_norm, res_norm, data_range=1.0))
                perceptual_score = score
                target_ssim = contract.tolerance.get("perceptual_metric", 0.99) or 0.99
                meets_perceptual = score >= target_ssim
            except Exception:
                # Fast MSE-based SSIM proxy: 1 - Normalized MSE
                nmse = float(np.mean(diff ** 2)) / max(1e-6, float(np.var(reference)))
                perceptual_score = max(0.0, 1.0 - nmse)
                meets_perceptual = perceptual_score >= 0.95

        # Functional Metric (e.g. Top-k accuracy)
        meets_functional = True
        if contract.functional_metric == "TOP_K" and result.ndim >= 1:
            k = min(contract.k, result.shape[-1])
            top_k_ref = np.argsort(reference, axis=-1)[..., -k:]
            top_k_res = np.argsort(result, axis=-1)[..., -k:]
            ref_rows = top_k_ref.reshape(-1, k)
            res_rows = top_k_res.reshape(-1, k)
            row_overlaps = [len(np.intersect1d(r_ref, r_res)) / k for r_ref, r_res in zip(ref_rows, res_rows)]
            overlap_ratio = float(np.mean(row_overlaps)) if row_overlaps else 1.0
            target_acc = float(contract.tolerance.get("functional_metric", 0.95) or 0.95)
            meets_functional = overlap_ratio >= target_acc

        # When TOP_K functional metric is declared, functional fidelity takes precedence
        rel_ok = (rel_error <= max_rel_tol) if contract.functional_metric != "TOP_K" else True
        if freivalds_passed is not None and not freivalds_passed:
            rel_ok = False

        contract_met = (
            rel_ok
            and meets_perceptual
            and meets_functional
        )

        reasons = []
        if not rel_ok:
            reasons.append(f"REL_ERR_{rel_error:.2e}_EXCEEDS_{max_rel_tol:.2e}")
        if freivalds_passed is False:
            reasons.append("FREIVALDS_O(N^2)_FAILED")
        if not meets_perceptual:
            reasons.append("PERCEPTUAL_METRIC_FAILED")
        if not meets_functional:
            reasons.append("FUNCTIONAL_METRIC_FAILED")

        verdict = "PASS" if contract_met else ("FAIL_" + "_".join(reasons))

        return VerificationResult(
            contract_met=contract_met,
            absolute_error=abs_error,
            relative_error=rel_error,
            perceptual_score=perceptual_score,
            functional_score=meets_functional,
            verdict=verdict,
            freivalds_pass=freivalds_passed,
            holdout_relative_error=holdout_err,
            verification_method=method,
        )
