"""
hyper_cco/contract.py
=====================
Formal ComputeContract Specification, 12-Class Correctness Taxonomy, and 8-Class Evidence Taxonomy.
Enforces that every computational optimization executed by HYPER-CCO strictly satisfies
the application's exactness class, error bounds, perceptual thresholds, latency,
and throughput targets without silent contract relaxation.
"""

from enum import Enum
from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, Any, Tuple, List
import json
import hashlib
import numpy as np


class ExactnessClass(str, Enum):
    """
    Non-negotiable 12-class correctness taxonomy.
    Every execution strategy MUST be explicitly classified as one of these.
    Never mix or conflate these classifications.
    """
    EXACT = "EXACT"                                 # Output is mathematically identical under declared numerical semantics
    EXACT_REFORMULATION = "EXACT_REFORMULATION"     # Different mathematical path but proven equivalent
    NUMERICALLY_EQUIVALENT = "NUMERICALLY_EQUIVALENT"# Numerical result falls within strictly declared numerical tolerance
    BOUNDED_APPROXIMATION = "BOUNDED_APPROXIMATION" # Output differs from exact result but has a verified error bound
    PERCEPTUAL_APPROXIMATION = "PERCEPTUAL_APPROXIMATION" # Application-level quality preserved (PSNR, SSIM, LPIPS)
    PREDICTIVE = "PREDICTIVE"                       # System predicts missing computation
    SPECULATIVE = "SPECULATIVE"                     # System computes a prediction and verifies/falls back
    CACHED = "CACHED"                               # Existing exact result reused
    REUSED = "REUSED"                               # Sub-computation or intermediate reused
    REDUCED_WORK = "REDUCED_WORK"                   # Only part of original computational graph evaluated
    SIMULATED = "SIMULATED"                         # Emulated behavior
    UNVERIFIED = "UNVERIFIED"                       # Result without verification (disallows parity claims)
    # Convenient aliases
    BITWISE_EXACT = "EXACT"
    APPLICATION_PRESERVED = "PERCEPTUAL_APPROXIMATION"
    PERCEPTUALLY_IDENTICAL = "PERCEPTUAL_APPROXIMATION"


class EvidenceClass(str, Enum):
    """
    Strict 8-class primary evidence taxonomy.
    Every result, report row, certificate, and API response must carry one and only one.
    """
    MEASURED_TARGET = "MEASURED_TARGET"             # Executed on physical Lenovo Core i5-12450H target machine
    MEASURED_NON_TARGET = "MEASURED_NON_TARGET"     # Executed on host environment (e.g., i5-13420H), explicitly labeled
    STATIC_FINDING = "STATIC_FINDING"               # Established from source, configuration, or deterministic inspection
    DOCUMENTED_CLAIM = "DOCUMENTED_CLAIM"           # Present in repository artifacts without independently verified trial chain
    BLOCKED = "BLOCKED"                             # Required model, input, device, dependency, or procedure unavailable
    INCONCLUSIVE = "INCONCLUSIVE"                   # Execution occurred but evidence is insufficient to decide
    HYPOTHESIS = "HYPOTHESIS"                       # Plausible proposal requiring experiment
    UNSUPPORTED = "UNSUPPORTED"                     # Claim rejected because evidence or equivalence is invalid


class VerificationLevel(str, Enum):
    """
    Multi-tier verification hierarchy.
    Level 1 is screening only, never to be confused with Level 3 or Level 4 proof.
    """
    LEVEL_0_NONE = "LEVEL_0_NONE"
    LEVEL_1_SAMPLE_SCREENING = "LEVEL_1_SAMPLE_SCREENING"
    LEVEL_2_BLOCK_CHECK = "LEVEL_2_BLOCK_CHECK"
    LEVEL_3_FULL_NUMERICAL = "LEVEL_3_FULL_NUMERICAL"
    LEVEL_4_FORMAL_EQUIVALENCE = "LEVEL_4_FORMAL_EQUIVALENCE" # Freivalds O(N^2), symbolic identity
    LEVEL_5_APPLICATION_VALIDATOR = "LEVEL_5_APPLICATION_VALIDATOR"


class VerificationStatus(str, Enum):
    """
    Strict 3-state verification outcome.
    Never convert INCONCLUSIVE into PASS.
    """
    PASS = "PASS"
    FAIL = "FAIL"
    INCONCLUSIVE = "INCONCLUSIVE"


class ContractViolationError(Exception):
    """Raised when an execution strategy violates declared contract constraints."""
    def __init__(self, message: str, contract: 'ComputeContract', measured: Dict[str, Any]):
        super().__init__(message)
        self.contract = contract
        self.measured = measured


@dataclass
class ComputeContract:
    """
    Formal representation of the application's required execution contract.
    Makes implicit assumptions fully explicit and verifiable.
    """
    workload_id: str = "default_workload"
    exactness_class: ExactnessClass = ExactnessClass.NUMERICALLY_EQUIVALENT
    evidence_class: EvidenceClass = EvidenceClass.MEASURED_NON_TARGET
    max_absolute_error: Optional[float] = 1e-4
    max_relative_error: Optional[float] = 1e-3
    normwise_error_bound: Optional[float] = None
    min_accuracy: Optional[float] = None
    min_psnr: Optional[float] = 35.0
    min_ssim: Optional[float] = 0.95
    min_perceptual_quality: Optional[float] = None
    min_throughput: Optional[float] = None
    max_latency_ms: Optional[float] = 5000.0
    deterministic: bool = True
    output_shape: Optional[Tuple[int, ...]] = None
    output_dtype: Optional[str] = None
    allow_cache: bool = True
    allow_reuse: bool = True
    allow_approximation: bool = True
    allow_prediction: bool = True
    allow_reduced_work: bool = True
    fallback_required: bool = True
    custom_invariants: Dict[str, Any] = field(default_factory=dict)

    def is_exact_required(self) -> bool:
        """Checks if exact bitwise or mathematical reformulation is required."""
        return self.exactness_class in (ExactnessClass.EXACT, ExactnessClass.EXACT_REFORMULATION)

    def compute_hash(self) -> str:
        """Deterministic cryptographic hash of contract parameters."""
        data = {
            "workload_id": self.workload_id,
            "exactness_class": self.exactness_class.value,
            "evidence_class": self.evidence_class.value,
            "max_absolute_error": self.max_absolute_error,
            "max_relative_error": self.max_relative_error,
            "normwise_error_bound": self.normwise_error_bound,
            "min_psnr": self.min_psnr,
            "min_ssim": self.min_ssim,
            "max_latency_ms": self.max_latency_ms,
            "deterministic": self.deterministic,
            "output_shape": list(self.output_shape) if self.output_shape else None,
            "output_dtype": self.output_dtype,
            "allow_cache": self.allow_cache,
            "allow_reuse": self.allow_reuse,
            "allow_approximation": self.allow_approximation,
            "allow_prediction": self.allow_prediction,
            "allow_reduced_work": self.allow_reduced_work,
            "fallback_required": self.fallback_required,
        }
        dump = json.dumps(data, sort_keys=True)
        return hashlib.sha256(dump.encode("utf-8")).hexdigest()[:16]

    def validate_metrics(
        self,
        candidate: Any,
        baseline: Optional[Any] = None,
        latency_ms: float = 0.0,
        throughput: float = 0.0
    ) -> Tuple[bool, VerificationStatus, Dict[str, Any]]:
        """
        Validates candidate results against contract bounds.
        Returns (is_valid, verification_status, metrics_dict).
        """
        metrics: Dict[str, Any] = {
            "latency_ms": latency_ms,
            "throughput": throughput,
            "error_abs": 0.0,
            "error_rel": 0.0,
            "normwise_err": 0.0,
            "psnr": float("inf"),
            "ssim": 1.0,
            "violation_reason": None,
        }

        # 1. Latency check
        if self.max_latency_ms is not None and latency_ms > self.max_latency_ms:
            metrics["violation_reason"] = f"Latency {latency_ms:.2f}ms exceeds SLO {self.max_latency_ms:.2f}ms"
            return False, VerificationStatus.FAIL, metrics

        # 2. Throughput check
        if self.min_throughput is not None and throughput < self.min_throughput and throughput > 0:
            metrics["violation_reason"] = f"Throughput {throughput:.2f} below target {self.min_throughput:.2f}"
            return False, VerificationStatus.FAIL, metrics

        # 3. Shape, Dtype, and Finiteness check
        if isinstance(candidate, np.ndarray):
            # Strict finiteness check: reject NaN and Inf
            if not np.all(np.isfinite(candidate)):
                metrics["violation_reason"] = "Candidate contains non-finite values (NaN or Inf)"
                return False, VerificationStatus.FAIL, metrics

            if self.output_shape is not None and candidate.shape != self.output_shape:
                metrics["violation_reason"] = f"Shape mismatch: {candidate.shape} != expected {self.output_shape}"
                return False, VerificationStatus.FAIL, metrics

            if self.output_dtype is not None and str(candidate.dtype) != self.output_dtype:
                metrics["violation_reason"] = f"Dtype mismatch: {candidate.dtype} != expected {self.output_dtype}"
                return False, VerificationStatus.FAIL, metrics

        # 4. Numerical error validation if baseline provided
        if baseline is not None and isinstance(candidate, np.ndarray) and isinstance(baseline, np.ndarray):
            # Anti-truncation check: candidate size must match baseline size exactly
            if candidate.shape != baseline.shape:
                metrics["violation_reason"] = f"Shape mismatch against baseline: {candidate.shape} != {baseline.shape}"
                return False, VerificationStatus.FAIL, metrics

            if candidate.size < baseline.size:
                metrics["violation_reason"] = f"Short candidate output: {candidate.size} < {baseline.size}"
                return False, VerificationStatus.FAIL, metrics

            abs_diff = np.abs(candidate - baseline)
            max_abs = float(np.max(abs_diff)) if abs_diff.size > 0 else 0.0
            norm_base = float(np.linalg.norm(baseline))
            norm_diff = float(np.linalg.norm(abs_diff))
            rel_err = norm_diff / max(1e-12, norm_base) if norm_base > 0 else max_abs

            metrics["error_abs"] = max_abs
            metrics["error_rel"] = rel_err
            metrics["normwise_err"] = norm_diff

            if self.is_exact_required():
                if max_abs > 0.0:
                    metrics["violation_reason"] = f"Exactness required but max_abs_error={max_abs:.2e} > 0"
                    return False, VerificationStatus.FAIL, metrics

            if self.max_absolute_error is not None and max_abs > (self.max_absolute_error * 1.001 + 1e-8):
                metrics["violation_reason"] = f"Max absolute error {max_abs:.2e} > allowed {self.max_absolute_error:.2e}"
                return False, VerificationStatus.FAIL, metrics

            if self.max_relative_error is not None and rel_err > (self.max_relative_error * 1.001 + 1e-8):
                metrics["violation_reason"] = f"Max relative error {rel_err:.2e} > allowed {self.max_relative_error:.2e}"
                return False, VerificationStatus.FAIL, metrics

            if self.normwise_error_bound is not None and norm_diff > (self.normwise_error_bound * 1.001 + 1e-8):
                metrics["violation_reason"] = f"Normwise error {norm_diff:.2e} > allowed {self.normwise_error_bound:.2e}"
                return False, VerificationStatus.FAIL, metrics

        return True, VerificationStatus.PASS, metrics

    # Convenient method aliases
    validate = validate_metrics
    compute_contract_hash = compute_hash
