"""
hyper_mvc_dar/heterogeneous_fabric.py
Heterogeneous Fabric: Schedules computation between Intel Core i5-12450H P-cores,
E-cores, and Intel UHD Graphics Xe Execution Units.
"""

from typing import Dict, Any, Tuple, List
import numpy as np


class HeterogeneousFabric:
    """Manages dynamic partitioning and device assignment across CPU + Intel iGPU."""

    @staticmethod
    def recommend_partition(m: int, n: int, k: int, arithmetic_intensity: float) -> Dict[str, Any]:
        """
        Determines the optimal CPU/iGPU split for large matrix or parallel operations.
        - For high arithmetic intensity (>15 FLOPs/byte) and large size: offload to iGPU.
        - For latency-critical small operations: pin 100% to CPU P-cores.
        """
        total_flops = 2 * m * n * k

        if total_flops < 50_000_000 or arithmetic_intensity < 2.0:
            # Latency bound -> CPU P-cores
            return {
                "cpu_ratio": 1.0,
                "igpu_ratio": 0.0,
                "preferred_device": "CPU_P_CORES",
                "reason": "Small working set or low arithmetic intensity; avoids kernel dispatch overhead"
            }
        elif total_flops > 500_000_000 and arithmetic_intensity >= 8.0:
            # High throughput parallel kernel -> Hybrid split
            return {
                "cpu_ratio": 0.40,
                "igpu_ratio": 0.60,
                "preferred_device": "HYBRID_CPU_IGPU",
                "reason": "Massive parallel batch; saturates both CPU AVX2 and iGPU execution units"
            }
        else:
            return {
                "cpu_ratio": 0.70,
                "igpu_ratio": 0.30,
                "preferred_device": "HYBRID_CPU_IGPU",
                "reason": "Balanced split based on 12450H TDP envelope"
            }

    @staticmethod
    def partition_workload_slices(total_items: int, cpu_ratio: float) -> Tuple[Tuple[int, int], Tuple[int, int]]:
        """Returns (cpu_start, cpu_end) and (igpu_start, igpu_end)."""
        cpu_count = int(total_items * cpu_ratio)
        return (0, cpu_count), (cpu_count, total_items)
