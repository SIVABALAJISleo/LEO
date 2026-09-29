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

from hyper.research_engine.exactness import ExactnessMode


@dataclasses.dataclass
class ProblemContract:
    workload_id: str
    description: str
    
    # Input / Output Domains
    input_domain: Dict[str, Any]       # e.g. {"A": {"shape": [M, K], "dtype": "FP32", "range": [-10.0, 10.0]}}
    output_domain: Dict[str, Any]      # e.g. {"C": {"shape": [M, N], "dtype": "FP32"}}
    valid_inputs_predicate: Optional[Callable[[Dict[str, Any]], bool]] = None
    
    # Requirements
    exactness_mode: ExactnessMode = ExactnessMode.NUMERIC_TOLERANCE
    tolerance_epsilon: float = 1e-4
    precision_requirement: str = "FP32"
    latency_limit_ms: float = 1000.0
    throughput_requirement: float = 1.0  # items/sec
    memory_limit_bytes: int = 4 * 1024 * 1024 * 1024  # 4 GB default limit
    power_limit_watts: float = 45.0                    # Laptop TDP default
    hardware_limits: Dict[str, Any] = dataclasses.field(default_factory=lambda: {
        "max_threads": 12,
        "use_igpu": True,
        "allow_remote": False,
    })
    determinism_requirement: bool = True
    side_effect_requirement: bool = False  # Pure functional by default
    
    def get_contract_hash(self) -> str:
        """Deterministic cryptographic hash representing the formal requirements."""
        meta = {
            "workload_id": self.workload_id,
            "input_domain": {k: str(v) for k, v in sorted(self.input_domain.items())},
            "output_domain": {k: str(v) for k, v in sorted(self.output_domain.items())},
            "exactness_mode": self.exactness_mode.value,
            "tolerance_epsilon": self.tolerance_epsilon,
            "precision_requirement": self.precision_requirement,
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

    def to_dict(self) -> Dict[str, Any]:
        return {
            "workload_id": self.workload_id,
            "description": self.description,
            "input_domain": self.input_domain,
            "output_domain": self.output_domain,
            "exactness_mode": self.exactness_mode.value,
            "tolerance_epsilon": self.tolerance_epsilon,
            "precision_requirement": self.precision_requirement,
            "latency_limit_ms": self.latency_limit_ms,
            "throughput_requirement": self.throughput_requirement,
            "memory_limit_bytes": self.memory_limit_bytes,
            "power_limit_watts": self.power_limit_watts,
            "hardware_limits": self.hardware_limits,
            "determinism_requirement": self.determinism_requirement,
            "side_effect_requirement": self.side_effect_requirement,
            "contract_hash": self.get_contract_hash(),
        }
