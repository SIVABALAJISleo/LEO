"""
hyper/research_engine/contracts.py
==================================
Formal Problem Contract Extraction & Validation Engine.

Extracts and models the authoritative specification of what computation the user
or program is asking the system to produce, independent of implementation details.
"""

from __future__ import annotations
import dataclasses
import hashlib
import json
from typing import Any, Callable, Dict, List, Optional, Tuple
import numpy as np

from hyper.research_engine.exactness import ExactnessCategory, ExactnessMode


@dataclasses.dataclass
class ComputationalContract:
    """
    Formal Computational Contract Engine.
    Defines the complete input/output specification, exactness requirements,
    tolerances, ordering constraints, determinism, and resource constraints for a workload.
    """
    workload_id: str
    description: str
    
    # Input / Output Domains
    input_domain: Dict[str, Any]       # e.g. {"A": {"shape": [M, K], "dtype": "FP32", "range": [-10.0, 10.0]}}
    output_domain: Dict[str, Any]      # e.g. {"C": {"shape": [M, N], "dtype": "FP32"}}
    valid_inputs_predicate: Optional[Callable[[Dict[str, Any]], bool]] = None
    
    # Exactness Requirements (EXACT, NUMERICALLY_EQUIVALENT, APPROXIMATE, HEURISTIC)
    exactness_category: ExactnessCategory = ExactnessCategory.NUMERICALLY_EQUIVALENT
    exactness_mode: ExactnessMode = ExactnessMode.NUMERIC_TOLERANCE
    tolerance_epsilon: float = 1e-4
    precision_requirement: str = "FP32"
    
    # Ordering & Determinism
    ordering_requirements: str = "STRICT_ORDER"  # STRICT_ORDER, ASSOCIATIVE_PERMITTED, COMMUTATIVE, ARBITRARY
    determinism_requirement: bool = True
    side_effect_requirement: bool = False        # Pure functional by default
    
    # Resource & Time Constraints
    latency_limit_ms: float = 1000.0
    time_constraints_ms: float = 1000.0
    throughput_requirement: float = 1.0          # items/sec
    memory_limit_bytes: int = 4 * 1024 * 1024 * 1024  # 4 GB default limit
    memory_constraints_bytes: int = 4 * 1024 * 1024 * 1024
    power_limit_watts: float = 45.0              # Laptop TDP default
    hardware_limits: Dict[str, Any] = dataclasses.field(default_factory=lambda: {
        "max_threads": 12,
        "use_igpu": True,
        "allow_remote": False,
    })

    def __post_init__(self):
        # Synchronize exactness category and mode
        if self.exactness_mode and not self.exactness_category:
            self.exactness_category = self.exactness_mode.to_category()
        elif self.exactness_category and not self.exactness_mode:
            if self.exactness_category == ExactnessCategory.EXACT:
                self.exactness_mode = ExactnessMode.NUMERIC_EXACT
            elif self.exactness_category == ExactnessCategory.NUMERICALLY_EQUIVALENT:
                self.exactness_mode = ExactnessMode.NUMERIC_TOLERANCE
            elif self.exactness_category == ExactnessCategory.APPROXIMATE:
                self.exactness_mode = ExactnessMode.PERCEPTUAL_EQUIVALENCE
            else:
                self.exactness_mode = ExactnessMode.CONTRACT_EQUIVALENCE

        # Sync legacy & upgraded fields
        if self.time_constraints_ms != 1000.0 and self.latency_limit_ms == 1000.0:
            self.latency_limit_ms = self.time_constraints_ms
        else:
            self.time_constraints_ms = self.latency_limit_ms

        if self.memory_constraints_bytes != 4 * 1024 * 1024 * 1024 and self.memory_limit_bytes == 4 * 1024 * 1024 * 1024:
            self.memory_limit_bytes = self.memory_constraints_bytes
        else:
            self.memory_constraints_bytes = self.memory_limit_bytes
    
    def get_contract_hash(self) -> str:
        """Deterministic cryptographic hash representing the formal requirements."""
        meta = {
            "workload_id": self.workload_id,
            "input_domain": {k: str(v) for k, v in sorted(self.input_domain.items())},
            "output_domain": {k: str(v) for k, v in sorted(self.output_domain.items())},
            "exactness_category": self.exactness_category.value,
            "exactness_mode": self.exactness_mode.value,
            "tolerance_epsilon": self.tolerance_epsilon,
            "precision_requirement": self.precision_requirement,
            "ordering_requirements": self.ordering_requirements,
            "latency_limit_ms": self.latency_limit_ms,
            "throughput_requirement": self.throughput_requirement,
            "memory_limit_bytes": self.memory_limit_bytes,
            "determinism_requirement": self.determinism_requirement,
            "side_effect_requirement": self.side_effect_requirement,
        }
        return hashlib.sha256(json.dumps(meta, sort_keys=True).encode("utf-8")).hexdigest()

    def validate_inputs(self, inputs: Dict[str, Any]) -> Tuple[bool, str]:
        """Validates that candidate inputs conform strictly to the declared input domain."""
        for param_name, domain in self.input_domain.items():
            if param_name not in inputs:
                return False, f"Missing required input parameter '{param_name}'"
            val = inputs[param_name]
            
            # Check shape if ndarray
            if isinstance(val, np.ndarray) and "shape" in domain:
                expected_shape = tuple(domain["shape"])
                if val.shape != expected_shape:
                    return False, f"Input '{param_name}' shape {val.shape} does not match expected {expected_shape}"
                    
            # Check range if defined
            if isinstance(val, np.ndarray) and "range" in domain:
                min_val, max_val = domain["range"]
                if np.any(np.isnan(val)) or np.any(np.isinf(val)):
                    if not domain.get("allow_nan_inf", False):
                        return False, f"Input '{param_name}' contains NaN or Inf which is disallowed"
                if np.any(val < min_val) or np.any(val > max_val):
                    return False, f"Input '{param_name}' values fall outside allowed range [{min_val}, {max_val}]"

        if self.valid_inputs_predicate:
            try:
                if not self.valid_inputs_predicate(inputs):
                    return False, "Custom valid_inputs_predicate evaluated to False"
            except Exception as e:
                return False, f"Custom valid_inputs_predicate error: {e}"

        return True, "Valid inputs"

    def validate_exactness(self, claimed_category: ExactnessCategory, measured_diff: float) -> Tuple[bool, str]:
        """
        Enforces exactness compliance. Never silently converts one category into another.
        """
        if claimed_category == ExactnessCategory.EXACT:
            if measured_diff > 0.0:
                return False, f"Claimed EXACT but measured non-zero difference {measured_diff}"
            return True, "Exact match verified (zero numerical/bit difference)"

        elif claimed_category == ExactnessCategory.NUMERICALLY_EQUIVALENT:
            if measured_diff > self.tolerance_epsilon:
                return False, f"Measured diff {measured_diff:.2e} exceeds contract epsilon {self.tolerance_epsilon:.2e}"
            return True, f"Numerically equivalent within epsilon {self.tolerance_epsilon:.2e}"

        elif claimed_category == ExactnessCategory.APPROXIMATE:
            return True, f"Approximate execution permitted (diff={measured_diff:.2e})"

        elif claimed_category == ExactnessCategory.HEURISTIC:
            return True, f"Heuristic execution permitted (diff={measured_diff:.2e})"

        return False, f"Unrecognized category {claimed_category}"

    def validate_output(self, output: Any, reference_output: Any) -> Tuple[bool, str, float]:
        """Validates output against independent reference output under contract rules."""
        if output is None or reference_output is None:
            return False, "Output or reference is None", float("inf")

        if isinstance(output, dict) and isinstance(reference_output, dict):
            max_err = 0.0
            for k in reference_output:
                if k not in output:
                    return False, f"Missing output key '{k}'", float("inf")
                sub_ok, sub_msg, sub_err = self._compare_values(output[k], reference_output[k])
                if not sub_ok:
                    return False, f"Key '{k}' mismatch: {sub_msg}", sub_err
                max_err = max(max_err, sub_err)
            return True, "All output keys match contract", max_err
        else:
            return self._compare_values(output, reference_output)

    def _compare_values(self, out: Any, ref: Any) -> Tuple[bool, str, float]:
        if isinstance(ref, np.ndarray) or isinstance(out, np.ndarray):
            out_arr = np.asarray(out)
            ref_arr = np.asarray(ref)
            if out_arr.shape != ref_arr.shape:
                return False, f"Shape mismatch {out_arr.shape} vs {ref_arr.shape}", float("inf")
            if np.issubdtype(out_arr.dtype, np.floating) and not np.all(np.isfinite(out_arr)):
                return False, "Output contains NaN or Inf", float("inf")
            max_diff = float(np.max(np.abs(out_arr - ref_arr)))
            ok, msg = self.validate_exactness(self.exactness_category, max_diff)
            return ok, msg, max_diff
        elif isinstance(ref, (int, float, np.integer, np.floating)):
            diff = float(abs(float(out) - float(ref)))
            ok, msg = self.validate_exactness(self.exactness_category, diff)
            return ok, msg, diff
        elif isinstance(ref, str):
            diff = 0.0 if out == ref else 1.0
            return (out == ref), ("Exact match" if out == ref else "String mismatch"), diff
        else:
            diff = 0.0 if out == ref else 1.0
            return (out == ref), ("Exact match" if out == ref else "Value mismatch"), diff

    def to_dict(self) -> Dict[str, Any]:
        return {
            "workload_id": self.workload_id,
            "description": self.description,
            "input_domain": self.input_domain,
            "output_domain": self.output_domain,
            "exactness_category": self.exactness_category.value,
            "exactness_mode": self.exactness_mode.value,
            "tolerance_epsilon": self.tolerance_epsilon,
            "precision_requirement": self.precision_requirement,
            "ordering_requirements": self.ordering_requirements,
            "latency_limit_ms": self.latency_limit_ms,
            "time_constraints_ms": self.time_constraints_ms,
            "throughput_requirement": self.throughput_requirement,
            "memory_limit_bytes": self.memory_limit_bytes,
            "memory_constraints_bytes": self.memory_constraints_bytes,
            "power_limit_watts": self.power_limit_watts,
            "hardware_limits": self.hardware_limits,
            "determinism_requirement": self.determinism_requirement,
            "side_effect_requirement": self.side_effect_requirement,
            "contract_hash": self.get_contract_hash(),
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> ComputationalContract:
        cat = ExactnessCategory(d.get("exactness_category", ExactnessCategory.NUMERICALLY_EQUIVALENT.value))
        mode = ExactnessMode(d.get("exactness_mode", ExactnessMode.NUMERIC_TOLERANCE.value))
        return cls(
            workload_id=d["workload_id"],
            description=d.get("description", ""),
            input_domain=dict(d.get("input_domain", {})),
            output_domain=dict(d.get("output_domain", {})),
            exactness_category=cat,
            exactness_mode=mode,
            tolerance_epsilon=float(d.get("tolerance_epsilon", 1e-4)),
            precision_requirement=str(d.get("precision_requirement", "FP32")),
            ordering_requirements=str(d.get("ordering_requirements", "STRICT_ORDER")),
            latency_limit_ms=float(d.get("latency_limit_ms", 1000.0)),
            time_constraints_ms=float(d.get("time_constraints_ms", d.get("latency_limit_ms", 1000.0))),
            throughput_requirement=float(d.get("throughput_requirement", 1.0)),
            memory_limit_bytes=int(d.get("memory_limit_bytes", 4 * 1024 * 1024 * 1024)),
            memory_constraints_bytes=int(d.get("memory_constraints_bytes", d.get("memory_limit_bytes", 4 * 1024 * 1024 * 1024))),
            power_limit_watts=float(d.get("power_limit_watts", 45.0)),
            hardware_limits=dict(d.get("hardware_limits", {})),
            determinism_requirement=bool(d.get("determinism_requirement", True)),
            side_effect_requirement=bool(d.get("side_effect_requirement", False)),
        )

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)

    @classmethod
    def from_json(cls, s: str) -> ComputationalContract:
        return cls.from_dict(json.loads(s))


# 100% Backward Compatibility Alias
ProblemContract = ComputationalContract

