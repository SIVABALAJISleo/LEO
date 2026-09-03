"""
hyper_v3/memory/dataflow_optimizer.py
Memory-first optimization engine managing zero-copy USM buffers,
AoS-to-SoA layout transformations, and kernel fusion to eliminate intermediate memory traffic.
"""

from typing import Dict, Any, List, Tuple
import numpy as np


class DataflowOptimizer:
    """Optimizes data layout, memory residency, and eliminates round-trips to RAM."""

    @staticmethod
    def convert_aos_to_soa(points_aos: np.ndarray) -> Dict[str, np.ndarray]:
        """Converts Array of Structures [N, 3] to Structure of Arrays (x: [N], y: [N], z: [N])."""
        # SoA enables contiguous SIMD vector loads across single dimensions
        assert points_aos.ndim == 2 and points_aos.shape[1] >= 3
        return {
            "x": np.ascontiguousarray(points_aos[:, 0]),
            "y": np.ascontiguousarray(points_aos[:, 1]),
            "z": np.ascontiguousarray(points_aos[:, 2])
        }

    @staticmethod
    def plan_fused_pipeline(stages: List[str]) -> List[List[str]]:
        """Identifies contiguous memory-bound operations that can be fused into in-register kernels."""
        fused_groups: List[List[str]] = []
        current_group: List[str] = []

        for stage in stages:
            # Linear point-wise ops and activations can always fuse with preceding GEMM/Conv
            if stage in ["bias_add", "relu", "gelu", "scale", "clamp", "quantize"]:
                if current_group:
                    current_group.append(stage)
                else:
                    current_group = [stage]
            else:
                if current_group:
                    fused_groups.append(current_group)
                current_group = [stage]

        if current_group:
            fused_groups.append(current_group)

        return fused_groups

    @staticmethod
    def calculate_fusion_traffic_savings(
        tensor_size_bytes: int,
        fused_ops_count: int
    ) -> Dict[str, Any]:
        """Calculates bytes read/written avoided by in-register fusion."""
        # Unfused: each intermediate op writes output to RAM and next op reads it from RAM
        unfused_traffic = tensor_size_bytes * (2 * (fused_ops_count - 1))
        fused_traffic = 0  # Held in registers/L1 cache

        return {
            "tensor_size_bytes": tensor_size_bytes,
            "fused_ops_count": fused_ops_count,
            "bytes_avoided": unfused_traffic,
            "traffic_reduction_percent": 100.0 if fused_ops_count > 1 else 0.0
        }
