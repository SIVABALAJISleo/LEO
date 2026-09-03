"""
hyper_v3/intelligence/bottleneck.py
Identifies whether a workload is compute-bound, memory-bound, transfer-bound, or launch-bound.
"""

from typing import Dict, Any
from hyper_v3.ir.node import IRNode


class BottleneckAnalyzer:
    """Profiles operational intensity (FLOPs/Byte) to classify bottlenecks."""

    @staticmethod
    def classify_node(node: IRNode, cpu_peak_gflops: float = 300.0, mem_bw_gbs: float = 40.0) -> Dict[str, Any]:
        flops = node.flops
        bytes_transferred = node.memory_reads_bytes + node.memory_writes_bytes

        if bytes_transferred == 0:
            return {"bottleneck": "COMPUTE_BOUND", "arithmetic_intensity": float("inf")}

        intensity = flops / max(bytes_transferred, 1)  # FLOPs / Byte
        machine_balance = cpu_peak_gflops / mem_bw_gbs  # Ridge point

        if intensity > machine_balance * 1.5:
            bottleneck = "COMPUTE_BOUND"
        elif intensity < machine_balance * 0.5:
            bottleneck = "MEMORY_BOUND"
        else:
            bottleneck = "BALANCED"

        return {
            "node_id": node.node_id,
            "flops": flops,
            "bytes_transferred": bytes_transferred,
            "arithmetic_intensity": float(intensity),
            "machine_ridge_point": float(machine_balance),
            "bottleneck": bottleneck
        }
