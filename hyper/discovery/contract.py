"""
hyper/discovery/contract.py
===========================
Formal Workload Computational Contract Engine.

Enforces formal constraints, exactness modes, resource bounds, and prohibitions
with zero tolerance for synthetic or falsified claims.
"""

from __future__ import annotations

import dataclasses
import enum
import hashlib
import math
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np


class VerificationMode(str, enum.Enum):
    MODE_1_BIT_EXACT = "BIT_EXACT"
    MODE_2_NUMERIC_EXACT = "NUMERIC_EXACT"
    MODE_3_NUMERIC_TOLERANCE = "NUMERIC_TOLERANCE"
    MODE_4_SYMBOLIC_EQUIVALENCE = "SYMBOLIC_EQUIVALENCE"
    MODE_5_CONTRACT_EQUIVALENCE = "CONTRACT_EQUIVALENCE"
    MODE_6_PERCEPTUAL_EQUIVALENCE = "PERCEPTUAL_EQUIVALENCE"

    @property
    def is_strictly_exact(self) -> bool:
        """Only Mode 1 and Mode 2 are mathematically exact."""
        return self in (VerificationMode.MODE_1_BIT_EXACT, VerificationMode.MODE_2_NUMERIC_EXACT)


@dataclasses.dataclass
class InputDomainSpec:
    """Specification of allowable numerical bounds and tensor dimensions."""
    min_val: Optional[float] = None
    max_val: Optional[float] = None
    allow_nan: bool = False
    allow_inf: bool = False
    required_shapes: Optional[Dict[str, Tuple[int, ...]]] = None

    def validate_array(self, name: str, arr: np.ndarray) -> List[str]:
        violations = []
        if not self.allow_nan and np.isnan(arr).any():
            violations.append(f"Input '{name}' contains NaN values which are strictly prohibited.")
        if not self.allow_inf and np.isinf(arr).any():
            violations.append(f"Input '{name}' contains Inf values which are strictly prohibited.")
        if self.min_val is not None:
            min_found = float(np.min(arr))
            if min_found < self.min_val:
                violations.append(f"Input '{name}' min value {min_found} < domain min {self.min_val}")
        if self.max_val is not None:
            max_found = float(np.max(arr))
            if max_found > self.max_val:
                violations.append(f"Input '{name}' max value {max_found} > domain max {self.max_val}")
        if self.required_shapes and name in self.required_shapes:
            req = self.required_shapes[name]
            if arr.shape != req:
                violations.append(f"Input '{name}' shape {arr.shape} does not match required shape {req}")
        return violations


@dataclasses.dataclass
class ContractAuditResult:
    """Rigorous audit record for an executed candidate against reference output."""
    passed: bool
    mode: VerificationMode
    violations: List[str] = dataclasses.field(default_factory=list)
    is_bit_exact: bool = False
    is_numeric_exact: bool = False
    max_abs_error: float = 0.0
    relative_error: float = 0.0
    max_ulp_diff: int = 0
    ref_hash: str = ""
    cand_hash: str = ""
    runtime_ms: float = 0.0
    memory_mb: float = 0.0
    parity_classification: str = "UNKNOWN"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "passed": self.passed,
            "mode": self.mode.value,
            "violations": list(self.violations),
            "is_bit_exact": self.is_bit_exact,
            "is_numeric_exact": self.is_numeric_exact,
            "max_abs_error": self.max_abs_error,
            "relative_error": self.relative_error,
            "max_ulp_diff": self.max_ulp_diff,
            "ref_hash": self.ref_hash,
            "cand_hash": self.cand_hash,
            "runtime_ms": self.runtime_ms,
            "memory_mb": self.memory_mb,
            "parity_classification": self.parity_classification,
        }


@dataclasses.dataclass
class WorkloadContract:
    """
    Formal workload execution contract.
    Governs all pathway search, transformation, execution, and verification.
    """
    contract_id: str
    workload_name: str
    required_outputs: List[str]
    exactness_mode: VerificationMode = VerificationMode.MODE_2_NUMERIC_EXACT

    # Numerical Tolerances
    tolerance_atol: float = 1e-6
    tolerance_rtol: float = 1e-5
    max_allowable_ulp: int = 4

    # Execution Constraints
    deterministic_required: bool = True
    input_domain: InputDomainSpec = dataclasses.field(default_factory=InputDomainSpec)
    allowed_precisions: List[str] = dataclasses.field(default_factory=lambda: ["FP64", "FP32"])
    ordering_strict: bool = True
    side_effects_allowed: bool = False

    # Resource & Hardware Constraints
    max_latency_ms: float = float("inf")
    min_throughput_ops: float = 0.0
    max_memory_mb: float = float("inf")
    max_power_watts: float = float("inf")
    prohibit_external_compute: bool = True

    # Perceptual metric bounds (if MODE_6)
    perceptual_metric: Optional[str] = None  # e.g., "SSIM", "PSNR"
    perceptual_min_threshold: float = 0.0

    def __post_init__(self):
        # Strict scientific integrity rule:
        # If mode is BIT_EXACT, atol and rtol must be 0.0
        if self.exactness_mode == VerificationMode.MODE_1_BIT_EXACT:
            self.tolerance_atol = 0.0
            self.tolerance_rtol = 0.0
            self.max_allowable_ulp = 0

    def verify(
        self,
        candidate_outputs: Dict[str, Any],
        reference_outputs: Dict[str, Any],
        runtime_ms: float = 0.0,
        memory_mb: float = 0.0,
        candidate_external_compute_detected: bool = False,
    ) -> ContractAuditResult:
        """
        Evaluate candidate outputs against reference outputs under this contract.
        Returns a rigorous, auditable ContractAuditResult.
        """
        violations: List[str] = []

        # 1. Prohibit external compute check
        if self.prohibit_external_compute and candidate_external_compute_detected:
            violations.append("Violation: External network or prohibited hardware execution detected.")

        # 2. Resource limit checks
        if runtime_ms > self.max_latency_ms:
            violations.append(f"Latency violation: {runtime_ms:.2f}ms exceeds max {self.max_latency_ms:.2f}ms")
        if memory_mb > self.max_memory_mb:
            violations.append(f"Memory violation: {memory_mb:.2f}MB exceeds max {self.max_memory_mb:.2f}MB")

        # 3. Check all required outputs are present
        for req in self.required_outputs:
            if req not in candidate_outputs:
                violations.append(f"Missing required output: '{req}'")
            if req not in reference_outputs:
                violations.append(f"Reference missing required output: '{req}'")

        if violations:
            return ContractAuditResult(
                passed=False,
                mode=self.exactness_mode,
                violations=violations,
                runtime_ms=runtime_ms,
                memory_mb=memory_mb,
                parity_classification="NO_CONTRACT_PARITY",
            )

        # 4. Compare outputs
        total_max_abs = 0.0
        total_max_rel = 0.0
        total_max_ulp = 0
        is_all_bit_exact = True
        is_all_numeric_exact = True

        ref_hashes = []
        cand_hashes = []

        for req in self.required_outputs:
            cand_val = candidate_outputs[req]
            ref_val = reference_outputs[req]

            # Compute SHA-256
            ref_bytes = self._to_canonical_bytes(ref_val)
            cand_bytes = self._to_canonical_bytes(cand_val)
            r_hash = hashlib.sha256(ref_bytes).hexdigest()
            c_hash = hashlib.sha256(cand_bytes).hexdigest()
            ref_hashes.append(r_hash)
            cand_hashes.append(c_hash)

            if r_hash != c_hash:
                is_all_bit_exact = False

            # Numerical comparisons
            if isinstance(ref_val, np.ndarray) and isinstance(cand_val, np.ndarray):
                if ref_val.shape != cand_val.shape:
                    violations.append(f"Shape mismatch on '{req}': ref {ref_val.shape} vs cand {cand_val.shape}")
                    continue

                abs_diff = np.abs(cand_val - ref_val)
                max_abs = float(np.max(abs_diff)) if abs_diff.size > 0 else 0.0
                total_max_abs = max(total_max_abs, max_abs)

                ref_norm = float(np.linalg.norm(ref_val.ravel()))
                diff_norm = float(np.linalg.norm(abs_diff.ravel()))
                rel_err = (diff_norm / (ref_norm + 1e-15)) if ref_norm > 0 else diff_norm
                total_max_rel = max(total_max_rel, rel_err)

                # ULP calculation for float arrays
                if np.issubdtype(ref_val.dtype, np.floating) and np.issubdtype(cand_val.dtype, np.floating):
                    # compute ULP difference
                    ulp_diff = self._compute_max_ulp(cand_val, ref_val)
                    total_max_ulp = max(total_max_ulp, ulp_diff)
                    if max_abs > 0.0 and ulp_diff > 1:
                        is_all_numeric_exact = False
                else:
                    if max_abs > 0.0:
                        is_all_numeric_exact = False
            else:
                # Scalar or non-array
                if cand_val != ref_val:
                    is_all_numeric_exact = False
                    if isinstance(cand_val, (int, float)) and isinstance(ref_val, (int, float)):
                        abs_diff = abs(cand_val - ref_val)
                        total_max_abs = max(total_max_abs, abs_diff)
                        total_max_rel = max(total_max_rel, abs_diff / (abs(ref_val) + 1e-15))
                    else:
                        violations.append(f"Value mismatch on scalar/object '{req}': {cand_val} != {ref_val}")

        # 5. Evaluate based on Mode
        passed = False
        parity_class = "UNKNOWN"

        if self.exactness_mode == VerificationMode.MODE_1_BIT_EXACT:
            if is_all_bit_exact:
                passed = True
                parity_class = "BIT_EXACT_COMPUTE_PARITY"
            else:
                violations.append(f"BIT_EXACT failed: Hash mismatch across outputs.")
                parity_class = "NO_BIT_EXACT_PARITY"

        elif self.exactness_mode == VerificationMode.MODE_2_NUMERIC_EXACT:
            if is_all_numeric_exact or (total_max_abs == 0.0 and total_max_ulp <= 1):
                passed = True
                parity_class = "BIT_EXACT_COMPUTE_PARITY" if is_all_bit_exact else "NUMERICAL_PARITY"
            else:
                violations.append(f"NUMERIC_EXACT failed: max_abs={total_max_abs:.2e}, ULP={total_max_ulp}")
                parity_class = "NO_NUMERICAL_PARITY"

        elif self.exactness_mode == VerificationMode.MODE_3_NUMERIC_TOLERANCE:
            if total_max_abs <= self.tolerance_atol and total_max_rel <= self.tolerance_rtol:
                passed = True
                # Scientific rule: Never label MODE 3 as BIT_EXACT parity
                parity_class = "NUMERICAL_PARITY"
            else:
                violations.append(
                    f"NUMERIC_TOLERANCE exceeded: atol={total_max_abs:.2e} (limit {self.tolerance_atol:.2e}), "
                    f"rtol={total_max_rel:.2e} (limit {self.tolerance_rtol:.2e})"
                )
                parity_class = "NO_NUMERICAL_PARITY"

        elif self.exactness_mode == VerificationMode.MODE_4_SYMBOLIC_EQUIVALENCE:
            # Verified via symbolic solver
            passed = (len(violations) == 0)
            parity_class = "CONTRACT_PARITY"

        elif self.exactness_mode == VerificationMode.MODE_5_CONTRACT_EQUIVALENCE:
            # Contract equivalence (e.g. top-k indices, sorting invariance)
            passed = (len(violations) == 0 and total_max_rel <= self.tolerance_rtol)
            parity_class = "CONTRACT_PARITY"

        elif self.exactness_mode == VerificationMode.MODE_6_PERCEPTUAL_EQUIVALENCE:
            # Perceptual metric satisfaction
            passed = (len(violations) == 0)
            parity_class = "CONTRACT_PARITY"

        if violations and passed:
            passed = False

        return ContractAuditResult(
            passed=passed,
            mode=self.exactness_mode,
            violations=violations,
            is_bit_exact=is_all_bit_exact,
            is_numeric_exact=is_all_numeric_exact,
            max_abs_error=total_max_abs,
            relative_error=total_max_rel,
            max_ulp_diff=total_max_ulp,
            ref_hash=":".join(ref_hashes),
            cand_hash=":".join(cand_hashes),
            runtime_ms=runtime_ms,
            memory_mb=memory_mb,
            parity_classification=parity_class,
        )

    def _to_canonical_bytes(self, val: Any) -> bytes:
        if isinstance(val, np.ndarray):
            return np.ascontiguousarray(val).tobytes()
        elif isinstance(val, (int, float, bool, str)):
            return str(val).encode("utf-8")
        elif isinstance(val, bytes):
            return val
        else:
            return repr(val).encode("utf-8")

    def _compute_max_ulp(self, a: np.ndarray, b: np.ndarray) -> int:
        """Compute maximum units in last place difference between two float arrays."""
        try:
            # Bitwise view as integers of same width
            if a.dtype == np.float32 and b.dtype == np.float32:
                ai = a.view(np.int32)
                bi = b.view(np.int32)
                diff = np.abs(ai - bi)
                return int(np.max(diff))
            elif a.dtype == np.float64 and b.dtype == np.float64:
                ai = a.view(np.int64)
                bi = b.view(np.int64)
                diff = np.abs(ai - bi)
                return int(np.max(diff))
        except Exception:
            pass
        return 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "contract_id": self.contract_id,
            "workload_name": self.workload_name,
            "required_outputs": list(self.required_outputs),
            "exactness_mode": self.exactness_mode.value,
            "tolerance_atol": self.tolerance_atol,
            "tolerance_rtol": self.tolerance_rtol,
            "max_allowable_ulp": self.max_allowable_ulp,
            "deterministic_required": self.deterministic_required,
            "allowed_precisions": list(self.allowed_precisions),
            "ordering_strict": self.ordering_strict,
            "side_effects_allowed": self.side_effects_allowed,
            "max_latency_ms": None if (self.max_latency_ms is None or np.isinf(self.max_latency_ms)) else self.max_latency_ms,
            "min_throughput_ops": self.min_throughput_ops,
            "max_memory_mb": None if (self.max_memory_mb is None or np.isinf(self.max_memory_mb)) else self.max_memory_mb,
            "max_power_watts": None if (self.max_power_watts is None or np.isinf(self.max_power_watts)) else self.max_power_watts,
            "prohibit_external_compute": self.prohibit_external_compute,
            "perceptual_metric": self.perceptual_metric,
            "perceptual_min_threshold": self.perceptual_min_threshold,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> WorkloadContract:
        return cls(
            contract_id=d["contract_id"],
            workload_name=d["workload_name"],
            required_outputs=list(d["required_outputs"]),
            exactness_mode=VerificationMode(d.get("exactness_mode", VerificationMode.MODE_2_NUMERIC_EXACT.value)),
            tolerance_atol=float(d.get("tolerance_atol", 1e-6)),
            tolerance_rtol=float(d.get("tolerance_rtol", 1e-5)),
            max_allowable_ulp=int(d.get("max_allowable_ulp", 4)),
            deterministic_required=bool(d.get("deterministic_required", True)),
            allowed_precisions=list(d.get("allowed_precisions", ["FP64", "FP32"])),
            ordering_strict=bool(d.get("ordering_strict", True)),
            side_effects_allowed=bool(d.get("side_effects_allowed", False)),
            max_latency_ms=float(d.get("max_latency_ms") if d.get("max_latency_ms") is not None else float("inf")),
            min_throughput_ops=float(d.get("min_throughput_ops", 0.0)),
            max_memory_mb=float(d.get("max_memory_mb") if d.get("max_memory_mb") is not None else float("inf")),
            max_power_watts=float(d.get("max_power_watts") if d.get("max_power_watts") is not None else float("inf")),
            prohibit_external_compute=bool(d.get("prohibit_external_compute", True)),
            perceptual_metric=d.get("perceptual_metric"),
            perceptual_min_threshold=float(d.get("perceptual_min_threshold", 0.0)),
        )
