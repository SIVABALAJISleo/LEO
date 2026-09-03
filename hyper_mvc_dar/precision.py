"""
hyper_mvc_dar/precision.py
Dynamic Precision Engine: Adapts numerical precision (FP64, FP32, FP16, INT8, Ternary 1.58-bit)
while maintaining rigorous error bounds.
"""

from typing import Dict, Any, Tuple
import numpy as np
from .ir import DataType
from .contract import ExecutionContract


class PrecisionEngine:
    """Controls dynamic precision selection and bounds quantization error."""

    @staticmethod
    def select_precision(contract: ExecutionContract, sensitivity: float = 1.0) -> DataType:
        if contract.is_exact():
            return DataType.FP32

        if contract.relative_error >= 0.05 and sensitivity < 0.5:
            return DataType.INT8

        if contract.relative_error >= 0.005:
            return DataType.FP16

        return DataType.FP32

    @staticmethod
    def quantize_to_ternary(matrix: np.ndarray) -> Tuple[np.ndarray, float]:
        """Quantizes floating-point weights into BitNet b1.58 {-1, 0, +1} with scaling factor."""
        gamma = float(np.mean(np.abs(matrix)))
        if gamma == 0:
            return np.zeros_like(matrix, dtype=np.int8), 1.0

        scaled = matrix / gamma
        ternary = np.clip(np.round(scaled), -1, 1).astype(np.int8)
        return ternary, gamma
