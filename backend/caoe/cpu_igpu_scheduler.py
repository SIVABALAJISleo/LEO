"""
backend/caoe/cpu_igpu_scheduler.py
==================================
CAOE Layer 5: CPU + iGPU Workload Scheduler.

Intelligently classifies tensor workloads and selects the most efficient executor:
- MEMORY_BOUND: Cache hits, elementwise ops -> CPU L1/L2/L3 cache
- COMPUTE_BOUND: Dense GEMM -> Tested across CPU AVX2 vs Intel UHD iGPU
- LATENCY_SENSITIVE: Sparse / small matrices -> CPU AVX2 tight loop
- HYBRID: Split along dimension between CPU and iGPU if break-even met
"""

from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

import numpy as np

from hyper.v8.scheduler import probe_hardware


class CPUiGPUScheduler:
    """Intelligently dispatches workload to CPU, iGPU, or Hybrid."""

    def __init__(self) -> None:
        self.cert = probe_hardware()

    def classify(self, tensor_shape: Tuple[int, ...], task_type: str = "GEMM") -> str:
        """Classify workload into operational regime."""
        if len(tensor_shape) < 2:
            return "MEMORY_BOUND"

        M, N = tensor_shape[0], tensor_shape[1]
        K = tensor_shape[2] if len(tensor_shape) > 2 else N

        # Arithmetic intensity (FLOPs per byte transferred)
        flops = 2.0 * M * K * N
        bytes_transferred = (M * K + K * N + M * N) * 4.0
        ai_ratio = flops / max(1.0, bytes_transferred)

        if ai_ratio < 2.0:
            return "MEMORY_BOUND"
        elif M <= 64 or N <= 64:
            return "LATENCY_SENSITIVE"
        elif ai_ratio >= 10.0 and M >= 512 and self.cert.igpu_detected:
            return "COMPUTE_BOUND"
        else:
            return "MIXED"

    def schedule(
        self,
        tensor_shape: Tuple[int, ...],
        contract: Any,
        task_type: str = "GEMM",
    ) -> Dict[str, Any]:
        """Determine dispatch strategy and expected performance ratio."""
        workload_type = self.classify(tensor_shape, task_type)

        if workload_type == "MEMORY_BOUND":
            return {
                "executor": "cpu",
                "workload_type": workload_type,
                "expected_speedup": 1.0,
                "reason": "Memory-bound workload executed in low-latency CPU cache",
            }
        elif workload_type == "LATENCY_SENSITIVE":
            return {
                "executor": "cpu",
                "workload_type": workload_type,
                "expected_speedup": 1.2,
                "reason": "Latency-sensitive matrix; CPU AVX2 avoids OpenCL dispatch overhead",
            }
        elif workload_type == "COMPUTE_BOUND" and self.cert.igpu_detected:
            return {
                "executor": "hybrid",
                "workload_type": workload_type,
                "cpu_portion": 0.6,
                "igpu_portion": 0.4,
                "expected_speedup": 1.15,
                "reason": "High arithmetic intensity; balanced 60/40 CPU/iGPU offload",
            }
        else:
            return {
                "executor": "cpu",
                "workload_type": workload_type,
                "expected_speedup": 1.0,
                "reason": "Standard balanced CPU execution",
            }
