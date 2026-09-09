"""
hyper_cco/precision_engine.py
=============================
Adaptive Precision & Quantization Engine.
Supports FP32, FP16, INT8 symmetric/affine, and Ternary 1.58-bit (BitNet {-1, 0, +1}).
Tracks precision conversions as workload transformations, analyzing numerical error,
quantization noise, and memory bandwidth reduction explicitly.
Never claims lower precision is exact without numerical proof.
"""

import time
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, Tuple, List, Callable
import numpy as np


class PrecisionFormat(str, Enum):
    FP32 = "FP32"
    FP16 = "FP16"
    INT8 = "INT8"
    INT4 = "INT4"
    TERNARY_BITNET = "TERNARY_BITNET" # {-1, 0, +1}


@dataclass
class PrecisionResult:
    """Telemetry and outcome of precision transformation."""
    output: np.ndarray
    input_format: PrecisionFormat
    internal_format: PrecisionFormat
    output_format: PrecisionFormat
    quantization_max_error: float
    relative_quantization_error: float
    memory_traffic_bytes_original: int
    memory_traffic_bytes_reduced: int
    memory_reduction_ratio: float
    original_operations: float
    executed_operations: float
    latency_ms: float
    contract_satisfied: bool
    strategy: str = "MIXED_PRECISION"


class PrecisionEngine:
    """
    Manages precision adaptation and quantization under contract error budgets.
    """

    @staticmethod
    def quantize_fp16(A: np.ndarray) -> Tuple[np.ndarray, float, float]:
        """Quantizes FP32 tensor to FP16 and measures quantization error."""
        A_f16 = A.astype(np.float16)
        A_reconstructed = A_f16.astype(np.float32)
        diff = np.abs(A - A_reconstructed)
        max_err = float(np.max(diff)) if diff.size > 0 else 0.0
        norm_A = float(np.linalg.norm(A))
        rel_err = float(np.linalg.norm(diff)) / max(1e-12, norm_A) if norm_A > 0 else max_err
        return A_f16, max_err, rel_err

    @staticmethod
    def quantize_int8_symmetric(A: np.ndarray) -> Tuple[np.ndarray, float, float, float]:
        """
        Symmetric INT8 quantization: scale = max(|A|) / 127.
        Returns (A_int8, scale, max_error, relative_error).
        """
        max_val = float(np.max(np.abs(A))) if A.size > 0 else 1.0
        scale = max_val / 127.0 if max_val > 0 else 1.0
        A_int8 = np.clip(np.round(A / max(1e-12, scale)), -128, 127).astype(np.int8)
        A_reconstructed = A_int8.astype(np.float32) * scale
        diff = np.abs(A - A_reconstructed)
        max_err = float(np.max(diff)) if diff.size > 0 else 0.0
        norm_A = float(np.linalg.norm(A))
        rel_err = float(np.linalg.norm(diff)) / max(1e-12, norm_A) if norm_A > 0 else max_err
        return A_int8, scale, max_err, rel_err

    @staticmethod
    def quantize_ternary_158(A: np.ndarray) -> Tuple[np.ndarray, float, float, float]:
        """
        BitNet 1.58b ternary quantization: values in {-1, 0, +1} scaled by mean(|A|).
        Returns (A_ternary, scale, max_error, relative_error).
        """
        scale = float(np.mean(np.abs(A))) if A.size > 0 else 1.0
        threshold = 0.5 * scale
        A_ternary = np.zeros_like(A, dtype=np.int8)
        A_ternary[A > threshold] = 1
        A_ternary[A < -threshold] = -1
        A_reconstructed = A_ternary.astype(np.float32) * scale
        diff = np.abs(A - A_reconstructed)
        max_err = float(np.max(diff)) if diff.size > 0 else 0.0
        norm_A = float(np.linalg.norm(A))
        rel_err = float(np.linalg.norm(diff)) / max(1e-12, norm_A) if norm_A > 0 else max_err
        return A_ternary, scale, max_err, rel_err

    @classmethod
    def execute_matmul_mixed_precision(
        cls,
        A: np.ndarray,
        B: np.ndarray,
        target_format: PrecisionFormat = PrecisionFormat.FP16,
        max_relative_error: float = 1e-3
    ) -> PrecisionResult:
        """
        Executes Y = A @ B using target precision format if quantization error
        satisfies contract bounds.
        """
        t0 = time.perf_counter()
        M, K = A.shape
        K2, N = B.shape
        orig_ops = 2.0 * M * K * N
        orig_bytes = A.nbytes + B.nbytes + (M * N * 4)

        if target_format == PrecisionFormat.FP16:
            A_f16, err_A, rel_A = cls.quantize_fp16(A)
            B_f16, err_B, rel_B = cls.quantize_fp16(B)
            rel_err_est = rel_A + rel_B

            if rel_err_est > max_relative_error:
                # Reject downcasting, fallback to FP32
                output = A @ B
                latency = (time.perf_counter() - t0) * 1000.0
                return PrecisionResult(
                    output=output,
                    input_format=PrecisionFormat.FP32,
                    internal_format=PrecisionFormat.FP32,
                    output_format=PrecisionFormat.FP32,
                    quantization_max_error=0.0,
                    relative_quantization_error=0.0,
                    memory_traffic_bytes_original=orig_bytes,
                    memory_traffic_bytes_reduced=orig_bytes,
                    memory_reduction_ratio=0.0,
                    original_operations=orig_ops,
                    executed_operations=orig_ops,
                    latency_ms=latency,
                    contract_satisfied=True,
                    strategy="PRECISION_REJECTED_FP32_FALLBACK"
                )

            # Execute FP16 matmul
            Y_f16 = A_f16 @ B_f16
            output = Y_f16.astype(np.float32)
            reduced_bytes = A_f16.nbytes + B_f16.nbytes + Y_f16.nbytes
            mem_red = 1.0 - (reduced_bytes / float(orig_bytes))
            latency = (time.perf_counter() - t0) * 1000.0

            return PrecisionResult(
                output=output,
                input_format=PrecisionFormat.FP32,
                internal_format=PrecisionFormat.FP16,
                output_format=PrecisionFormat.FP32,
                quantization_max_error=max(err_A, err_B),
                relative_quantization_error=rel_err_est,
                memory_traffic_bytes_original=orig_bytes,
                memory_traffic_bytes_reduced=reduced_bytes,
                memory_reduction_ratio=mem_red,
                original_operations=orig_ops,
                executed_operations=orig_ops, # operations count same, but 16-bit vector lane throughput doubled
                latency_ms=latency,
                contract_satisfied=True,
                strategy="MIXED_PRECISION_FP16"
            )

        elif target_format == PrecisionFormat.INT8:
            A_i8, s_A, err_A, rel_A = cls.quantize_int8_symmetric(A)
            B_i8, s_B, err_B, rel_B = cls.quantize_int8_symmetric(B)
            rel_err_est = rel_A + rel_B

            if rel_err_est > max_relative_error:
                output = A @ B
                latency = (time.perf_counter() - t0) * 1000.0
                return PrecisionResult(
                    output=output,
                    input_format=PrecisionFormat.FP32,
                    internal_format=PrecisionFormat.FP32,
                    output_format=PrecisionFormat.FP32,
                    quantization_max_error=0.0,
                    relative_quantization_error=0.0,
                    memory_traffic_bytes_original=orig_bytes,
                    memory_traffic_bytes_reduced=orig_bytes,
                    memory_reduction_ratio=0.0,
                    original_operations=orig_ops,
                    executed_operations=orig_ops,
                    latency_ms=latency,
                    contract_satisfied=True,
                    strategy="PRECISION_REJECTED_FP32_FALLBACK"
                )

            # Execute INT8 integer dot product and scale back
            Y_i32 = A_i8.astype(np.int32) @ B_i8.astype(np.int32)
            output = Y_i32.astype(np.float32) * (s_A * s_B)
            reduced_bytes = A_i8.nbytes + B_i8.nbytes + (M * N)
            mem_red = 1.0 - (reduced_bytes / float(orig_bytes))
            latency = (time.perf_counter() - t0) * 1000.0

            return PrecisionResult(
                output=output,
                input_format=PrecisionFormat.FP32,
                internal_format=PrecisionFormat.INT8,
                output_format=PrecisionFormat.FP32,
                quantization_max_error=max(err_A, err_B),
                relative_quantization_error=rel_err_est,
                memory_traffic_bytes_original=orig_bytes,
                memory_traffic_bytes_reduced=reduced_bytes,
                memory_reduction_ratio=mem_red,
                original_operations=orig_ops,
                executed_operations=orig_ops,
                latency_ms=latency,
                contract_satisfied=True,
                strategy="MIXED_PRECISION_INT8"
            )

        # Default fallback
        output = A @ B
        latency = (time.perf_counter() - t0) * 1000.0
        return PrecisionResult(
            output=output,
            input_format=PrecisionFormat.FP32,
            internal_format=PrecisionFormat.FP32,
            output_format=PrecisionFormat.FP32,
            quantization_max_error=0.0,
            relative_quantization_error=0.0,
            memory_traffic_bytes_original=orig_bytes,
            memory_traffic_bytes_reduced=orig_bytes,
            memory_reduction_ratio=0.0,
            original_operations=orig_ops,
            executed_operations=orig_ops,
            latency_ms=latency,
            contract_satisfied=True,
            strategy="PRECISION_FP32_DEFAULT"
        )
