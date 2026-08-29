"""
hyper100/precision_engine.py
============================
Contract-Aware Precision Optimization Engine.
Dynamically maps operations to FP32, FP16, INT8, or 1.58-bit Ternary representations,
bounding mathematical error and rejecting downcasting that violates the contract.
"""

import time
from enum import Enum
from typing import Dict, Any, Tuple, Optional
from dataclasses import dataclass
import numpy as np

from .contract_engine import ExecutionContract, ContractViolationError


class PrecisionFormat(str, Enum):
    FP32 = "FP32"
    FP16 = "FP16"
    INT8 = "INT8"
    TERNARY_1_58 = "TERNARY_1_58"


@dataclass
class PrecisionReport:
    """Quantitative measurement of precision optimization."""
    format: PrecisionFormat
    bytes_per_element: float
    memory_compression_ratio: float
    max_absolute_error: float
    relative_error: float
    satisfies_contract: bool
    simulated_speedup: float


class PrecisionEngine:
    """Executes dynamic precision quantization and execution."""

    @staticmethod
    def quantize_int8(tensor: np.ndarray) -> Tuple[np.ndarray, float, float]:
        """
        Symmetric INT8 linear quantization: q = clip(round(x / scale), -127, 127).
        Returns: (q_tensor_int8, scale, dequant_error)
        """
        arr = np.asarray(tensor, dtype=np.float32)
        max_val = float(np.max(np.abs(arr)))
        scale = max_val / 127.0 if max_val > 0 else 1.0
        q = np.clip(np.round(arr / scale), -127, 127).astype(np.int8)
        dequant = q.astype(np.float32) * scale
        err = float(np.max(np.abs(arr - dequant)))
        return q, scale, err

    @staticmethod
    def quantize_ternary_1_58(tensor: np.ndarray) -> Tuple[np.ndarray, float, float]:
        """
        BitNet-style 1.58-bit ternary quantization: W_ternary in {-1, 0, +1}
        with absmean scaling gamma = mean(|W|).
        """
        arr = np.asarray(tensor, dtype=np.float32)
        gamma = float(np.mean(np.abs(arr)))
        if gamma > 0:
            scaled = arr / gamma
            q = np.clip(np.round(scaled), -1, 1).astype(np.int8)
            dequant = q.astype(np.float32) * gamma
        else:
            q = np.zeros_like(arr, dtype=np.int8)
            dequant = np.zeros_like(arr, dtype=np.float32)
        err = float(np.max(np.abs(arr - dequant)))
        return q, gamma, err

    @classmethod
    def optimize_precision(
        cls,
        tensor: np.ndarray,
        contract: ExecutionContract,
        preferred_format: Optional[PrecisionFormat] = None
    ) -> Tuple[np.ndarray, PrecisionFormat, PrecisionReport]:
        """
        Finds the lowest precision format that strictly satisfies the contract.
        """
        arr = np.asarray(tensor, dtype=np.float32)
        norm_orig = float(np.linalg.norm(arr))

        candidate_formats = [
            PrecisionFormat.TERNARY_1_58,
            PrecisionFormat.INT8,
            PrecisionFormat.FP16,
            PrecisionFormat.FP32
        ]
        if preferred_format:
            candidate_formats = [preferred_format] + [f for f in candidate_formats if f != preferred_format]

        for fmt in candidate_formats:
            if fmt == PrecisionFormat.TERNARY_1_58:
                q, gamma, max_err = cls.quantize_ternary_1_58(arr)
                dequant = q.astype(np.float32) * gamma
                bytes_elem = 0.25  # ~2 bits
                speedup = 4.0
            elif fmt == PrecisionFormat.INT8:
                q, scale, max_err = cls.quantize_int8(arr)
                dequant = q.astype(np.float32) * scale
                bytes_elem = 1.0
                speedup = 2.5
            elif fmt == PrecisionFormat.FP16:
                dequant = arr.astype(np.float16).astype(np.float32)
                max_err = float(np.max(np.abs(arr - dequant)))
                bytes_elem = 2.0
                speedup = 1.8
            else:  # FP32
                dequant = arr
                max_err = 0.0
                bytes_elem = 4.0
                speedup = 1.0

            rel_err = float(np.linalg.norm(arr - dequant) / (norm_orig + 1e-12)) if norm_orig > 0 else 0.0
            valid = (max_err <= contract.max_error and rel_err <= contract.max_relative_error) if not contract.is_exact_required() else (max_err == 0.0)

            if valid or fmt == PrecisionFormat.FP32:
                comp_ratio = 4.0 / bytes_elem
                report = PrecisionReport(
                    format=fmt,
                    bytes_per_element=bytes_elem,
                    memory_compression_ratio=comp_ratio,
                    max_absolute_error=max_err,
                    relative_error=rel_err,
                    satisfies_contract=valid,
                    simulated_speedup=speedup
                )
                return dequant, fmt, report

        # Fallback to FP32
        report = PrecisionReport(
            format=PrecisionFormat.FP32,
            bytes_per_element=4.0,
            memory_compression_ratio=1.0,
            max_absolute_error=0.0,
            relative_error=0.0,
            satisfies_contract=True,
            simulated_speedup=1.0
        )
        return arr, PrecisionFormat.FP32, report
