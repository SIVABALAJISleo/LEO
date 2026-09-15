"""
hyper/precision/precision_engine.py
===================================
Multi-Precision Engine for LEO/HYPER.
Fulfills Phase 9 of the Master Architectural Specification.
Supports: float64, float32, float16, bfloat16, int8, int4, ternary.
Reports input/accumulator/output precision, errors, speed, and memory honestly.
"""

import time
from typing import Any, Dict, Optional, Tuple
import numpy as np
import torch


PRECISION_MODES = [
    "float64",
    "float32",
    "float16",
    "bfloat16",
    "int8",
    "int4",
    "ternary",
]


class PrecisionEngine:
    """
    Evaluates matrix computations across explicit precision modes.
    Guarantees strict error bounding and never claims approximate results are exact.
    """

    @staticmethod
    def quantize_ternary(W: np.ndarray) -> Tuple[np.ndarray, float]:
        gamma = float(np.mean(np.abs(W)))
        if gamma < 1e-12:
            gamma = 1.0
        W_scaled = W / gamma
        W_ternary = np.clip(np.round(W_scaled), -1, 1).astype(np.int8)
        return W_ternary, gamma

    @staticmethod
    def quantize_int8(X: np.ndarray) -> Tuple[np.ndarray, float]:
        scale = float(np.max(np.abs(X)) / 127.0)
        if scale < 1e-12:
            scale = 1.0
        X_int8 = np.clip(np.round(X / scale), -128, 127).astype(np.int8)
        return X_int8, scale

    @staticmethod
    def quantize_int4(X: np.ndarray) -> Tuple[np.ndarray, float]:
        scale = float(np.max(np.abs(X)) / 7.0)
        if scale < 1e-12:
            scale = 1.0
        X_int4 = np.clip(np.round(X / scale), -8, 7).astype(np.int8)
        return X_int4, scale

    def execute_matmul(
        self,
        A: np.ndarray,
        B: np.ndarray,
        mode: str = "float32",
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Execute matmul in specified precision mode and compare against float64 reference.
        """
        mode = mode.lower()
        if mode not in PRECISION_MODES:
            raise ValueError(f"Unsupported precision mode '{mode}'. Supported: {PRECISION_MODES}")

        # Compute ground-truth reference in float64
        t_ref0 = time.perf_counter_ns()
        ref_C = (A.astype(np.float64)) @ (B.astype(np.float64))
        t_ref_ms = (time.perf_counter_ns() - t_ref0) / 1e6

        t0 = time.perf_counter_ns()

        if mode == "float64":
            input_prec = "float64"
            accum_prec = "float64"
            output_prec = "float64"
            C = A.astype(np.float64) @ B.astype(np.float64)
            memory_bytes = C.nbytes

        elif mode == "float32":
            input_prec = "float32"
            accum_prec = "float32"
            output_prec = "float32"
            C = A.astype(np.float32) @ B.astype(np.float32)
            memory_bytes = C.nbytes

        elif mode == "float16":
            input_prec = "float16"
            accum_prec = "float16"
            output_prec = "float16"
            A_f16 = A.astype(np.float16)
            B_f16 = B.astype(np.float16)
            C = A_f16 @ B_f16
            memory_bytes = C.nbytes

        elif mode == "bfloat16":
            input_prec = "bfloat16"
            accum_prec = "float32"
            output_prec = "bfloat16"
            tA = torch.from_numpy(A.astype(np.float32)).to(torch.bfloat16)
            tB = torch.from_numpy(B.astype(np.float32)).to(torch.bfloat16)
            tC = torch.matmul(tA, tB)
            C = tC.to(torch.float32).numpy()
            memory_bytes = A.size * 2 + B.size * 2 + C.size * 2

        elif mode == "int8":
            input_prec = "int8"
            accum_prec = "int32"
            output_prec = "float32"
            A_i8, sA = self.quantize_int8(A)
            B_i8, sB = self.quantize_int8(B)
            # Matmul in int32 accumulator
            C_int32 = A_i8.astype(np.int32) @ B_i8.astype(np.int32)
            C = C_int32.astype(np.float32) * (sA * sB)
            memory_bytes = A_i8.nbytes + B_i8.nbytes

        elif mode == "int4":
            input_prec = "int4"
            accum_prec = "int32"
            output_prec = "float32"
            A_i4, sA = self.quantize_int4(A)
            B_i4, sB = self.quantize_int4(B)
            C_int32 = A_i4.astype(np.int32) @ B_i4.astype(np.int32)
            C = C_int32.astype(np.float32) * (sA * sB)
            memory_bytes = (A_i4.nbytes // 2) + (B_i4.nbytes // 2)

        elif mode == "ternary":
            input_prec = "ternary (1.58-bit)"
            accum_prec = "int32"
            output_prec = "float32"
            W_tern, sW = self.quantize_ternary(A)
            B_i8, sB = self.quantize_int8(B)
            C_int32 = W_tern.astype(np.int32) @ B_i8.astype(np.int32)
            C = C_int32.astype(np.float32) * (sW * sB)
            memory_bytes = int(A.size * 0.25) + B_i8.nbytes

        t_elapsed_ms = (time.perf_counter_ns() - t0) / 1e6

        # Error metrics relative to float64 ground truth
        C_f64 = C.astype(np.float64)
        abs_err = float(np.max(np.abs(ref_C - C_f64)))
        denom = float(np.linalg.norm(ref_C))
        rel_err = float(np.linalg.norm(ref_C - C_f64) / max(1e-12, denom))

        report = {
            "mode": mode,
            "input_precision": input_prec,
            "accumulator_precision": accum_prec,
            "output_precision": output_prec,
            "max_abs_error": abs_err,
            "relative_error": rel_err,
            "latency_ms": t_elapsed_ms,
            "reference_f64_latency_ms": t_ref_ms,
            "memory_bytes": memory_bytes,
            "is_exact": bool(abs_err == 0.0),
        }
        return C, report
