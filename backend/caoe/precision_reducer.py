"""
backend/caoe/precision_reducer.py
=================================
CAOE Layer 2: Precision Reducer & Dynamic Quantization.

Negotiates precision down to the lowest acceptable level (FP32 -> FP16 -> INT8)
that satisfies the contract's relative/absolute error bound.
"""

from __future__ import annotations

import time
from typing import Any, Callable, Dict, List, Tuple

import numpy as np

from .contract_analyzer import Contract


class PrecisionReducer:
    """Negotiate precision down to acceptable level."""

    @staticmethod
    def apply_precision(tensor: np.ndarray, target_precision: int) -> Tuple[np.ndarray, float]:
        """
        Apply precision downscaling:
        - 32: FP32
        - 16: IEEE float16
        - 8:  symmetric INT8 quantization with scale factor
        Returns (quantized_or_cast_tensor, scale)
        """
        if target_precision == 16:
            return tensor.astype(np.float16), 1.0
        elif target_precision == 8:
            max_val = float(np.max(np.abs(tensor)))
            scale = max(1e-9, max_val / 127.0)
            int8_data = np.clip(np.round(tensor / scale), -128, 127).astype(np.int8)
            # Return dequantized reconstruction for direct numerical pipeline compatibility
            return (int8_data.astype(np.float32) * scale), scale
        return tensor.astype(np.float32), 1.0

    @classmethod
    def reduce_iteratively(
        cls,
        computation_fn: Callable[[np.ndarray, int], np.ndarray],
        sample_inputs: List[np.ndarray],
        contract: Contract,
    ) -> Dict[str, Any]:
        """
        Evaluate full computation at FP32, then step down to FP16 and INT8.
        Selects the lowest precision that stays within the contract relative error.
        """
        inp = sample_inputs[0] if sample_inputs else np.zeros((16, 16), dtype=np.float32)

        # Baseline: FP32
        t0 = time.perf_counter_ns()
        reference = computation_fn(inp, 32)
        ref_ms = max(1e-6, (time.perf_counter_ns() - t0) / 1e6)

        max_allowed_err = float(contract.tolerance.get("relative_error", 1e-4) or 1e-4)

        for target_prec in [8, 16]:  # Try cheapest first
            t0 = time.perf_counter_ns()
            reduced = computation_fn(inp, target_prec)
            reduced_ms = max(1e-6, (time.perf_counter_ns() - t0) / 1e6)

            diff = np.abs(reduced.astype(np.float64) - reference.astype(np.float64))
            ref_abs = np.abs(reference.astype(np.float64))
            with np.errstate(divide="ignore", invalid="ignore"):
                rel = np.where(ref_abs > 0, diff / ref_abs, diff)
            err = float(np.max(rel)) if rel.size > 0 else 0.0

            if err <= max_allowed_err:
                speedup = ref_ms / reduced_ms
                return {
                    "precision": target_prec,
                    "error": err,
                    "speedup": round(speedup, 2),
                    "acceptable": True,
                }

        # If reduced precision violates contract, remain at FP32
        return {"precision": 32, "error": 0.0, "speedup": 1.0, "acceptable": True}
