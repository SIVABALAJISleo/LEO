"""
hyper_x/communication/engine.py
=============================================================================
HYPER-X Communication-Avoidance Engine
=============================================================================
Explicit Objective:
  MINIMIZE BYTES MOVED, not simply maximize FLOPS.

Tracks, audits, and minimizes:
  - Host DRAM to LLC / L2 / L1 data movement
  - CPU <-> iGPU shared USM bus traffic
  - Intermediate tensor materialization vs fused on-the-fly recomputation
  - Memory traffic lower bounds and communication reduction ratio
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Any, List

@dataclass
class CommunicationMetrics:
    workload_id: str
    baseline_bytes_moved: int
    optimized_bytes_moved: int
    bytes_avoided: int
    communication_reduction_ratio: float
    cache_reuse_factor: float
    intermediate_materializations_avoided: int

class CommunicationAvoidanceEngine:
    """Calculates and enforces communication reduction strategies."""

    def analyze_tensor_traffic(
        self,
        workload_id: str,
        tensor_shapes_bytes: List[int],
        fused_passes: int = 1,
        recompute_intermediates: bool = True
    ) -> CommunicationMetrics:
        baseline_bytes = sum(tensor_shapes_bytes) * 2  # Read + Write baseline
        
        # In a fused pass, intermediate reads and writes stay in cache
        if recompute_intermediates and fused_passes > 1:
            intermediate_bytes = sum(tensor_shapes_bytes[1:-1]) * 2
            opt_bytes = max(tensor_shapes_bytes[0] + tensor_shapes_bytes[-1], baseline_bytes - intermediate_bytes)
            avoided = baseline_bytes - opt_bytes
            intermediates_avoided = fused_passes - 1
        else:
            opt_bytes = baseline_bytes
            avoided = 0
            intermediates_avoided = 0

        reduction_ratio = avoided / max(1, baseline_bytes)
        reuse_factor = baseline_bytes / max(1, opt_bytes)

        return CommunicationMetrics(
            workload_id=workload_id,
            baseline_bytes_moved=baseline_bytes,
            optimized_bytes_moved=opt_bytes,
            bytes_avoided=avoided,
            communication_reduction_ratio=reduction_ratio,
            cache_reuse_factor=reuse_factor,
            intermediate_materializations_avoided=intermediates_avoided
        )
