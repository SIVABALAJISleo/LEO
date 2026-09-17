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

    def as_dict(self) -> Dict[str, Any]:
        return {
            "contract_met": self.contract_met,
            "absolute_error": float(f"{self.absolute_error:.3e}"),
            "relative_error": float(f"{self.relative_error:.3e}"),
            "perceptual_score": round(self.perceptual_score, 4) if self.perceptual_score is not None else None,
            "functional_score": self.functional_score,
            "verdict": self.verdict,
        }


class Verifier:
    """Measure: Did we meet the contract?"""

    @staticmethod
    def verify(
        result: np.ndarray,
        reference: np.ndarray,
        contract: Contract,
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
            )

        # Numerical Error
        diff = np.abs(result.astype(np.float64) - reference.astype(np.float64))
        abs_error = float(np.max(diff)) if diff.size > 0 else 0.0

        ref_abs = np.abs(reference.astype(np.float64))
        with np.errstate(divide="ignore", invalid="ignore"):
            rel = np.where(ref_abs > 0, diff / ref_abs, diff)
        rel_error = float(np.max(rel)) if rel.size > 0 else 0.0

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
            overlap = np.intersect1d(top_k_ref.flatten(), top_k_res.flatten())
            overlap_ratio = len(overlap) / max(1, top_k_ref.size)
            target_acc = contract.tolerance.get("functional_metric", 0.95) or 0.95
            meets_functional = overlap_ratio >= target_acc

        max_rel_tol = float(contract.tolerance.get("relative_error", 1e-4) or 1e-4)
        contract_met = (
            rel_error <= max_rel_tol
            and meets_perceptual
            and meets_functional
        )

        reasons = []
        if rel_error > max_rel_tol:
            reasons.append(f"REL_ERR_{rel_error:.2e}_EXCEEDS_{max_rel_tol:.2e}")
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
        )
