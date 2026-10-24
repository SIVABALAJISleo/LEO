"""
hyper_phase_change/cost_model.py
================================
Analytical and Empirical Cost Model for Phase-Change and Accelerator Selection.

Accounts for:
- FLOP count and theoretical arithmetic intensity.
- Memory bandwidth consumption and intermediate allocation pressure.
- Detection overhead from structural tensor inspection.
- Kernel compilation / OpenVINO graph build overhead vs. steady-state execution.
- Host-to-Device transfer / unified memory synchronization overhead.
- Regression avoidance: rejects candidate transformations if net speedup <= 1.0.
"""

from __future__ import annotations

import dataclasses
from typing import Any, Dict, List, Optional, Tuple
import numpy as np


@dataclasses.dataclass
class CostProfile:
    """Detailed cost profile for a candidate execution path."""
    workload_id: str
    backend_id: str
    estimated_flops: float
    memory_read_bytes: int
    memory_write_bytes: int
    arithmetic_intensity: float  # FLOPs / Byte
    detection_overhead_ms: float
    compilation_overhead_ms: float
    transfer_overhead_ms: float
    estimated_exec_ms: float
    total_projected_latency_ms: float
    is_regression_risk: bool
    notes: List[str] = dataclasses.field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "workload_id": self.workload_id,
            "backend_id": self.backend_id,
            "estimated_flops": self.estimated_flops,
            "memory_read_bytes": self.memory_read_bytes,
            "memory_write_bytes": self.memory_write_bytes,
            "arithmetic_intensity": round(self.arithmetic_intensity, 4),
            "detection_overhead_ms": round(self.detection_overhead_ms, 4),
            "compilation_overhead_ms": round(self.compilation_overhead_ms, 4),
            "transfer_overhead_ms": round(self.transfer_overhead_ms, 4),
            "estimated_exec_ms": round(self.estimated_exec_ms, 4),
            "total_projected_latency_ms": round(self.total_projected_latency_ms, 4),
            "is_regression_risk": self.is_regression_risk,
            "notes": self.notes,
        }


class PhaseChangeCostModel:
    """
    Evaluates execution alternatives against baseline CPU cost.
    Ensures zero regressions: if optimization overhead exceeds execution savings,
    the cost model flags a regression risk and advises baseline fallback.
    """

    # Estimated peak hardware limits for Intel Core i5-12450H & Intel UHD Graphics
    # Peak memory bandwidth ~ 51.2 GB/s (DDR5/LPDDR5 dual channel)
    PEAK_MEMORY_BANDWIDTH_GB_S = 51.2
    # Effective memory bandwidth factor (considering contention & cache hierarchy)
    EFFECTIVE_BW_FACTOR = 0.65

    @classmethod
    def estimate_flops(cls, workload_id: str, inputs: Dict[str, Any]) -> float:
        """Estimates required FLOPs for canonical workloads based on input dimensions."""
        if workload_id == "GEMM_TILED":
            A = inputs.get("A")
            B = inputs.get("B")
            if A is not None and B is not None:
                m, k = A.shape
                _, n = B.shape
                return 2.0 * m * n * k
            return 2.0 * 256 * 256 * 256

        elif workload_id == "CONV2D_WINOGRAD":
            x = inputs.get("x")
            w = inputs.get("w")
            if x is not None and w is not None:
                b, c_in, h, w_w = x.shape
                c_out, _, kh, kw = w.shape
                h_out = h - kh + 1
                w_out = w_w - kw + 1
                return 2.0 * b * c_out * c_in * h_out * w_out * kh * kw
            return 2.0 * 1 * 16 * 3 * 32 * 32 * 3 * 3

        elif workload_id == "ATTENTION_FLASH":
            q = inputs.get("q")
            if q is not None:
                b, n, h, d = q.shape
                # Q @ K.T: 2 * b * h * n * n * d
                # Softmax @ V: 2 * b * h * n * n * d
                return 4.0 * b * h * n * n * d
            return 4.0 * 1 * 128 * 4 * 64 * 128

        elif workload_id == "ML_MLP_INFERENCE":
            X = inputs.get("X")
            W1 = inputs.get("W1")
            W2 = inputs.get("W2")
            if X is not None and W1 is not None and W2 is not None:
                f1 = 2.0 * X.shape[0] * W1.shape[0] * W1.shape[1]  # X @ W1
                f2 = 2.0 * X.shape[0] * W2.shape[0] * W2.shape[1]  # H @ W2
                return f1 + f2
            return 2.0 * 64 * 128 * 64 + 2.0 * 64 * 64 * 64

        elif workload_id in ("REDUCTION_SUM", "PREFIX_SCAN"):
            x = inputs.get("x")
            if x is not None:
                return float(x.size)
            return 100000.0

        elif workload_id == "IMAGE_SOBEL":
            img = inputs.get("image")
            if img is not None:
                return float(img.size * 18)  # 2 3x3 kernels
            return 512.0 * 512.0 * 18

        return 10000.0

    @classmethod
    def calculate_memory_bytes(cls, inputs: Dict[str, Any]) -> Tuple[int, int]:
        """Calculates input read bytes and estimated output write bytes."""
        read_bytes = 0
        for val in inputs.values():
            if isinstance(val, np.ndarray):
                read_bytes += val.nbytes
            elif isinstance(val, (int, float)):
                read_bytes += 8
        # Output write estimate (typically 20-50% of input size or scalar)
        write_bytes = max(8, read_bytes // 2)
        return read_bytes, write_bytes

    @classmethod
    def evaluate_cost(
        cls,
        workload_id: str,
        backend_id: str,
        inputs: Dict[str, Any],
        detection_overhead_ms: float = 0.0,
        compilation_overhead_ms: float = 0.0,
        baseline_latency_ms: Optional[float] = None,
    ) -> CostProfile:
        """
        Evaluates projected cost for a given backend or phase-change rewrite.
        Flags regression risk if projected latency > baseline_latency_ms.
        """
        flops = cls.estimate_flops(workload_id, inputs)
        read_bytes, write_bytes = cls.calculate_memory_bytes(inputs)
        total_bytes = read_bytes + write_bytes

        intensity = flops / max(1.0, float(total_bytes))

        # Memory transfer / cache cost estimate
        effective_bw_bytes_per_ms = (cls.PEAK_MEMORY_BANDWIDTH_GB_S * 1e9 * cls.EFFECTIVE_BW_FACTOR) / 1000.0
        memory_latency_ms = total_bytes / max(1.0, effective_bw_bytes_per_ms)

        # Baseline execution estimate
        if backend_id == "PHASE_CHANGE_ELIMINATION":
            exec_ms = 0.005  # Constant time shortcut
            transfer_ms = 0.0
        elif backend_id == "OPENVINO_IGPU":
            # GPU kernel execution + synchronization
            exec_ms = (flops / 1e8) * 0.8  # Scaled by GPU GFLOPS
            transfer_ms = memory_latency_ms * 0.4  # Zero-copy shared RAM sync
        else:  # CPU_AVX2 / NumPy
            exec_ms = (flops / 5e7) * 1.0  # Scaled by AVX2 CPU GFLOPS
            transfer_ms = 0.0

        total_latency = detection_overhead_ms + compilation_overhead_ms + transfer_ms + exec_ms

        notes = []
        is_regression = False
        if baseline_latency_ms is not None and baseline_latency_ms > 0:
            if total_latency > baseline_latency_ms:
                is_regression = True
                notes.append(
                    f"Regression detected: Projected {total_latency:.3f}ms exceeds baseline {baseline_latency_ms:.3f}ms. "
                    "Overhead of optimization exceeds execution savings."
                )
            else:
                speedup = baseline_latency_ms / total_latency
                notes.append(f"Projected speedup: {speedup:.2f}x over baseline.")

        return CostProfile(
            workload_id=workload_id,
            backend_id=backend_id,
            estimated_flops=flops,
            memory_read_bytes=read_bytes,
            memory_write_bytes=write_bytes,
            arithmetic_intensity=intensity,
            detection_overhead_ms=detection_overhead_ms,
            compilation_overhead_ms=compilation_overhead_ms,
            transfer_overhead_ms=transfer_ms,
            estimated_exec_ms=exec_ms,
            total_projected_latency_ms=total_latency,
            is_regression_risk=is_regression,
            notes=notes,
        )
