"""
hyper_universal/precision/optimizer.py
Memory-Aware and Numerical Precision Optimizer:
Evaluates FP32, FP16, INT8, and BitNet b1.58 Ternary formats,
strictly tracking quantization error (RMSE/max_err) against contract limits.
"""
from __future__ import annotations
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Tuple
import numpy as np


class PrecisionFormat(str, Enum):
    FP32 = "FP32"
    FP16 = "FP16"
    INT8 = "INT8"
    TERNARY_B158 = "TERNARY_B158"


@dataclass
class PrecisionReport:
    format: PrecisionFormat
    original_bytes: int
    compressed_bytes: int
    compression_ratio: float
    quantization_rmse: float
    max_absolute_error: float
    is_lossless: bool
    conversion_latency_ms: float
    contract_passed: bool

    def to_dict(self) -> Dict[str, Any]:
        return {
            "format": self.format.value,
            "original_bytes": self.original_bytes,
            "compressed_bytes": self.compressed_bytes,
            "compression_ratio": round(self.compression_ratio, 2),
            "quantization_rmse": round(self.quantization_rmse, 6),
            "max_absolute_error": round(self.max_absolute_error, 6),
            "is_lossless": self.is_lossless,
            "conversion_latency_ms": round(self.conversion_latency_ms, 3),
            "contract_passed": self.contract_passed,
        }


class PrecisionOptimizer:
    """Evaluates and applies precision transformations."""

    @staticmethod
    def quantize_int8(
        tensor: np.ndarray, max_allowed_error: float = 0.05
    ) -> Tuple[np.ndarray, float, PrecisionReport]:
        """Symmetric INT8 linear quantization."""
        t0 = time.perf_counter()
        orig_bytes = tensor.nbytes
        abs_max = float(np.max(np.abs(tensor))) + 1e-12
        scale = abs_max / 127.0

        q_int8 = np.clip(np.round(tensor / scale), -128, 127).astype(np.int8)
        reconstructed = q_int8.astype(np.float32) * scale

        diff = np.abs(tensor - reconstructed)
        max_abs = float(np.max(diff))
        rmse = float(np.sqrt(np.mean(diff ** 2)))
        conv_time_ms = (time.perf_counter() - t0) * 1000.0

        comp_bytes = q_int8.nbytes
        report = PrecisionReport(
            format=PrecisionFormat.INT8,
            original_bytes=orig_bytes,
            compressed_bytes=comp_bytes,
            compression_ratio=orig_bytes / max(comp_bytes, 1),
            quantization_rmse=rmse,
            max_absolute_error=max_abs,
            is_lossless=False,
            conversion_latency_ms=conv_time_ms,
            contract_passed=max_abs <= max_allowed_error,
        )
        return q_int8, scale, report

    @staticmethod
    def quantize_fp16(
        tensor: np.ndarray, max_allowed_error: float = 1e-3
    ) -> Tuple[np.ndarray, PrecisionReport]:
        """IEEE FP16 half-precision casting."""
        t0 = time.perf_counter()
        orig_bytes = tensor.nbytes
        f16 = tensor.astype(np.float16)
        reconstructed = f16.astype(np.float32)

        diff = np.abs(tensor - reconstructed)
        max_abs = float(np.max(diff))
        rmse = float(np.sqrt(np.mean(diff ** 2)))
        conv_time_ms = (time.perf_counter() - t0) * 1000.0

        comp_bytes = f16.nbytes
        report = PrecisionReport(
            format=PrecisionFormat.FP16,
            original_bytes=orig_bytes,
            compressed_bytes=comp_bytes,
            compression_ratio=orig_bytes / max(comp_bytes, 1),
            quantization_rmse=rmse,
            max_absolute_error=max_abs,
            is_lossless=False,
            conversion_latency_ms=conv_time_ms,
            contract_passed=max_abs <= max_allowed_error,
        )
        return f16, report
