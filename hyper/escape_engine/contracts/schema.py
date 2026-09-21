"""
hyper/escape_engine/contracts/schema.py
======================================
Formal Machine-Readable Computational Contract Schema for VAEE.
Defines explicit correctness, domain, tolerance, determinism, and resource bounds.
"""

from __future__ import annotations

import dataclasses
import hashlib
import json
from typing import Any, Dict, List, Optional, Tuple


@dataclasses.dataclass
class ComputationalContract:
    contract_id: str
    input_type: str                   # e.g., "matrix", "vector", "polynomial", "graph", "sequence"
    output_type: str                  # e.g., "matrix", "scalar", "vector", "permutation"
    input_shape: Tuple[int, ...]
    output_shape: Tuple[int, ...]
    dtype: str = "float32"
    correctness: str = "EXACT"        # "EXACT" | "NUMERICAL" | "INVARIANT" | "APPROXIMATE"
    numeric_tolerance: float = 0.0    # 0.0 for exact; >0.0 for numerical tolerance
    relative_tolerance: float = 0.0
    deterministic: bool = True
    acceptable_approximations: List[str] = dataclasses.field(default_factory=list)
    forbidden_approximations: List[str] = dataclasses.field(default_factory=list)
    side_effects: bool = False
    max_latency_ms: Optional[float] = None
    max_memory_mb: Optional[float] = None
    max_energy_j: Optional[float] = None
    verification_method: str = "EXACT_DIFFERENTIAL" # "EXACT" | "EXACT_DIFFERENTIAL" | "INVARIANT" | "FREIVALDS"
    perceptual_metric: Optional[str] = None
    functional_metric: Optional[str] = None
    k: int = 5

    def contract_hash(self) -> str:
        """Compute cryptographic hash of contract constraints."""
        h = hashlib.sha256()
        h.update(self.contract_id.encode())
        h.update(self.input_type.encode())
        h.update(self.output_type.encode())
        h.update(str(self.input_shape).encode())
        h.update(str(self.output_shape).encode())
        h.update(self.correctness.encode())
        h.update(str(self.numeric_tolerance).encode())
        h.update(str(self.relative_tolerance).encode())
        h.update(str(self.deterministic).encode())
        return h.hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return dataclasses.asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ComputationalContract:
        # Convert list shapes to tuples if needed
        data = dict(data)
        if "input_shape" in data and isinstance(data["input_shape"], list):
            data["input_shape"] = tuple(data["input_shape"])
        if "output_shape" in data and isinstance(data["output_shape"], list):
            data["output_shape"] = tuple(data["output_shape"])
        return cls(**data)
