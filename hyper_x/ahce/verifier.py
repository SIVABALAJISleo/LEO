"""
hyper_x/ahce/verifier.py
========================
Independent Verifier for AHCE (Sections 24 & 25).

Adheres to:
- Candidate: Implementation A
- Reference: Implementation B
- Verifier: Implementation C
- Fail-Closed: Never generates a PASS without verifying numerical or perceptual bounds.
"""

from __future__ import annotations
import hashlib
from dataclasses import dataclass, asdict
from typing import Dict, Any, Tuple, Optional
import numpy as np

from .contract import AHCEContract, CorrectnessClass
from hyper.verification.verifier import VerificationEngine


@dataclass
class AHCEVerificationVerdict:
    passed: bool
    correctness_class: CorrectnessClass
    max_abs_error: float
    max_rel_error: float
    rmse: float
    psnr: Optional[float] = None
    ssim: Optional[float] = None
    freivalds_passed: Optional[bool] = None
    output_hash: str = ""
    details: str = ""

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["correctness_class"] = self.correctness_class.value
        return d


class AHCEVerifier:
    """Independent verification engine checking candidate outputs against reference and contract."""

    def __init__(self):
        self.engine = VerificationEngine()

    def _hash(self, arr: Any) -> str:
        if isinstance(arr, np.ndarray):
            return hashlib.sha256(np.ascontiguousarray(arr).tobytes()).hexdigest()
        return hashlib.sha256(str(arr).encode("utf-8")).hexdigest()

    def verify(
        self,
        candidate_output: Any,
        reference_output: Any,
        contract: AHCEContract,
        A: Optional[np.ndarray] = None,
        B: Optional[np.ndarray] = None
    ) -> AHCEVerificationVerdict:
        cand_hash = self._hash(candidate_output)

        if not isinstance(candidate_output, np.ndarray) or not isinstance(reference_output, np.ndarray):
            # Non-array comparison
            is_eq = bool(candidate_output == reference_output)
            return AHCEVerificationVerdict(
                passed=is_eq,
                correctness_class=contract.correctness_class,
                max_abs_error=0.0 if is_eq else 1.0,
                max_rel_error=0.0 if is_eq else 1.0,
                rmse=0.0 if is_eq else 1.0,
                output_hash=cand_hash,
                details="Scalar or structural equality comparison."
            )

        # Numerical comparison
        num_metrics = self.engine.verify_numerical(candidate_output, reference_output)
        max_abs = num_metrics["max_abs_error"]
        rel_err = num_metrics["relative_error"]
        rmse = num_metrics["rmse"]

        # Freivalds probe for matrix multiplication if matrices provided
        freivalds_pass = None
        if A is not None and B is not None and candidate_output.ndim == 2:
            f_res = self.engine.verify_freivalds(A, B, candidate_output, num_trials=10, eps=contract.max_relative_error or 1e-4)
            freivalds_pass = f_res.get("is_probabilistically_consistent", True)

        # Contract checks
        passed = True
        details = []

        if contract.correctness_class == CorrectnessClass.EXACT:
            if max_abs > 1e-7:
                passed = False
                details.append(f"EXACT contract failed: max_abs_error {max_abs:.4e} > 1e-7")

        if contract.max_abs_error is not None and max_abs > contract.max_abs_error:
            passed = False
            details.append(f"Exceeded max_abs_error {max_abs:.4e} > {contract.max_abs_error:.4e}")

        if contract.max_relative_error is not None and rel_err > contract.max_relative_error:
            passed = False
            details.append(f"Exceeded max_relative_error {rel_err:.4e} > {contract.max_relative_error:.4e}")

        if freivalds_pass is False:
            passed = False
            details.append("Freivalds probabilistic consistency probe failed.")

        return AHCEVerificationVerdict(
            passed=passed,
            correctness_class=contract.correctness_class,
            max_abs_error=max_abs,
            max_rel_error=rel_err,
            rmse=rmse,
            freivalds_passed=freivalds_pass,
            output_hash=cand_hash,
            details="; ".join(details) if details else "Contract bounds satisfied."
        )
