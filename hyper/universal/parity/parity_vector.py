"""
hyper/universal/parity/parity_vector.py
=======================================
12-Dimensional Parity Vector and Parity Tier Classification.
Parity Vector:
P(W) = (
    latency,
    throughput,
    memory,
    bandwidth,
    energy,
    power,
    scalability,
    correctness,
    precision,
    reliability,
    utilization,
    workload_coverage
)
Rule: Maintain strict separation between HARDWARE, ALGORITHMIC, COMPUTATIONAL,
CONTRACT, PERFORMANCE, and UNIVERSAL parity.
"""

from __future__ import annotations

import dataclasses
from enum import Enum
from typing import Any, Dict, Optional


class ParityClass(str, Enum):
    HARDWARE_PARITY = "HARDWARE_PARITY"                 # Physical silicon specs (FLOP/s, bus width, raw execution units)
    ALGORITHMIC_PARITY = "ALGORITHMIC_PARITY"           # Work elimination ratio (W_hyper / W_ref)
    COMPUTATIONAL_PARITY = "COMPUTATIONAL_PARITY"       # End-to-end task throughput under arbitrary pathways
    CONTRACT_PARITY = "CONTRACT_PARITY"                 # 100% binary contract condition satisfaction
    PERFORMANCE_PARITY = "PERFORMANCE_PARITY"           # Latency speedup and throughput matching
    UNIVERSAL_PARITY = "UNIVERSAL_PARITY"               # Parity across arbitrary unseen workloads


@dataclasses.dataclass
class ParityVector:
    latency_ms: float
    throughput_ops_per_sec: float
    memory_peak_mb: float
    bandwidth_gb_per_sec: float
    energy_mj: float
    power_watts: float
    scalability_efficiency: float      # Scaling efficiency with workload size [0.0, 1.0]
    correctness_binary: bool           # PASS / FAIL
    precision_bits: int                # 64, 32, 16, 8, 2
    reliability_pct: float             # Invariant and reproducibility rate [0.0, 100.0]
    hardware_utilization_pct: float    # CPU / iGPU saturation percentage
    workload_coverage_pct: float       # Supported domains coverage percentage

    def to_dict(self) -> Dict[str, Any]:
        return dataclasses.asdict(self)
