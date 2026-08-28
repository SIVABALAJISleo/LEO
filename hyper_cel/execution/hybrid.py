"""
hyper_cel/execution/hybrid.py
=============================================================================
HYPER-CEL: Overlapped CPU + iGPU Hybrid Execution Pipeline (Mode C)
=============================================================================
Overlaps CPU preparation/verification with iGPU parallel execution:
    T_total ~= max(T_CPU, T_iGPU) < (T_CPU + T_iGPU)
"""

import time
import numpy as np
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Any, Tuple, Callable, List
from hyper_cel.execution.cpu import CPUExecutionBackend
from hyper_cel.execution.igpu import iGPUExecutionBackend

class HybridCPUiGPUPipeline:
    """Manages overlapped asynchronous CPU + iGPU compute streams."""

    def __init__(self):
        self.cpu = CPUExecutionBackend()
        self.igpu = iGPUExecutionBackend()
        self.executor = ThreadPoolExecutor(max_workers=4)

    def execute_overlapped_layers(
        self,
        layers: List[Dict[str, Any]],
        layer_weights: List[np.ndarray],
        input_state: np.ndarray
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Executes sequence of layers with CPU pre-processing of Layer N+1 overlapped
        with iGPU GEMM execution of Layer N.
        """
        t0 = time.perf_counter()
        current_state = np.copy(input_state)
        num_layers = len(layers)

        cpu_prep_times = []
        igpu_compute_times = []

        # Pre-process first layer on CPU
        t_prep_start = time.perf_counter()
        prep_weight_0 = np.ascontiguousarray(layer_weights[0])
        cpu_prep_times.append((time.perf_counter() - t_prep_start) * 1000.0)

        for l_idx in range(num_layers):
            current_weight = prep_weight_0 if l_idx == 0 else prep_weight_next

            # Launch CPU prep of next layer asynchronously (if not last layer)
            if l_idx + 1 < num_layers:
                future_next_prep = self.executor.submit(
                    lambda idx: np.ascontiguousarray(layer_weights[idx]),
                    l_idx + 1
                )

            # Execute current layer on iGPU
            t_igpu_start = time.perf_counter()
            out_tensor, _ = self.igpu.execute_dense_gemm(current_state, current_weight)
            current_state = np.copy(out_tensor)
            igpu_compute_times.append((time.perf_counter() - t_igpu_start) * 1000.0)

            # Retrieve next prep result
            if l_idx + 1 < num_layers:
                prep_weight_next = future_next_prep.result()

        t1 = time.perf_counter()
        total_latency_ms = (t1 - t0) * 1000.0
        sum_sequential_ms = sum(cpu_prep_times) + sum(igpu_compute_times)
        overlap_efficiency_pct = max(0.0, (1.0 - (total_latency_ms / max(0.001, sum_sequential_ms)))) * 100.0

        return current_state, {
            "mode": "HYBRID_CPU_iGPU_OVERLAP",
            "layers_executed": num_layers,
            "total_latency_ms": round(total_latency_ms, 3),
            "sum_sequential_ms": round(sum_sequential_ms, 3),
            "overlap_efficiency_pct": round(overlap_efficiency_pct, 2)
        }
