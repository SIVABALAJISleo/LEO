"""
hyper/universal/contracts/universal_contract.py
===============================================
Universal Computational Contract schema.
Formally specifies requirements: input/output, exactness, precision, tolerances,
determinism, side effects, latency, throughput, memory, energy, and perceptual quality.
Rule: Never silently weaken the contract.
"""

from __future__ import annotations

import dataclasses
from enum import Enum
from typing import Any, Dict, List, Optional


class ContractCorrectness(str, Enum):
    EXACT = "EXACT"
    NUMERICAL = "NUMERICAL"
    BOUNDED_ERROR = "BOUNDED_ERROR"
    APPROXIMATE = "APPROXIMATE"


class PrecisionTier(str, Enum):
    FLOAT64 = "FLOAT64"
    FLOAT32 = "FLOAT32"
    FLOAT16 = "FLOAT16"
    INT32 = "INT32"
    INT16 = "INT16"
    INT8 = "INT8"
    TERNARY = "TERNARY"
    BINARY = "BINARY"
    EXACT_INTEGER = "EXACT_INTEGER"


@dataclasses.dataclass
class UniversalContract:
    contract_id: str
    workload_id: str
    correctness: ContractCorrectness = ContractCorrectness.EXACT
    precision: PrecisionTier = PrecisionTier.FLOAT32
    numeric_tolerance: float = 0.0
    relative_tolerance: float = 0.0
    deterministic: bool = True
    side_effects: bool = False
    stateful: bool = False
    latency_requirement_ms: Optional[float] = None
    throughput_requirement_ops: Optional[float] = None
    memory_requirement_mb: Optional[float] = None
    energy_requirement_j: Optional[float] = None
    quality_requirements: Dict[str, float] = dataclasses.field(default_factory=dict)
    acceptable_approximations: List[str] = dataclasses.field(default_factory=list)
    forbidden_approximations: List[str] = dataclasses.field(default_factory=list)
    verification_method: str = "AUTO"

    def is_exact(self) -> bool:
        return self.correctness == ContractCorrectness.EXACT and self.numeric_tolerance == 0.0 and self.relative_tolerance == 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "contract_id": self.contract_id,
            "workload_id": self.workload_id,
            "correctness": self.correctness.value,
            "precision": self.precision.value,
            "numeric_tolerance": self.numeric_tolerance,
            "relative_tolerance": self.relative_tolerance,
            "deterministic": self.deterministic,
            "side_effects": self.side_effects,
            "stateful": self.stateful,
            "latency_requirement_ms": self.latency_requirement_ms,
            "throughput_requirement_ops": self.throughput_requirement_ops,
            "memory_requirement_mb": self.memory_requirement_mb,
            "energy_requirement_j": self.energy_requirement_j,
            "quality_requirements": self.quality_requirements,
            "acceptable_approximations": self.acceptable_approximations,
            "forbidden_approximations": self.forbidden_approximations,
            "verification_method": self.verification_method,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> UniversalContract:
        return cls(
            contract_id=d["contract_id"],
            workload_id=d.get("workload_id", "unknown"),
            correctness=ContractCorrectness(d.get("correctness", "EXACT")),
            precision=PrecisionTier(d.get("precision", "FLOAT32")),
            numeric_tolerance=float(d.get("numeric_tolerance", 0.0)),
            relative_tolerance=float(d.get("relative_tolerance", 0.0)),
            deterministic=bool(d.get("deterministic", True)),
            side_effects=bool(d.get("side_effects", False)),
            stateful=bool(d.get("stateful", False)),
            latency_requirement_ms=d.get("latency_requirement_ms"),
            throughput_requirement_ops=d.get("throughput_requirement_ops"),
            memory_requirement_mb=d.get("memory_requirement_mb"),
            energy_requirement_j=d.get("energy_requirement_j"),
            quality_requirements=d.get("quality_requirements", {}),
            acceptable_approximations=d.get("acceptable_approximations", []),
            forbidden_approximations=d.get("forbidden_approximations", []),
            verification_method=d.get("verification_method", "AUTO"),
        )
