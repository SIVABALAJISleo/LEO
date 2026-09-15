"""
hyper_x/ahce/domains/ai.py
==========================
AI and Vision domain adapter for AHCE.
"""

from typing import Dict, Any, Tuple
import numpy as np
from ..contract import AHCEContract, CorrectnessClass


class AIDomainAdapter:
    """AI feature extraction and neural embedding adapter."""

    def execute_feature_projection(
        self,
        features: np.ndarray,
        projection_weights: np.ndarray,
        contract: AHCEContract
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        # Tiled vector projection with INT8 dynamic scale
        if contract.allow_approximation and features.ndim == 2:
            # Scaled quantization
            scale_f = float(np.max(np.abs(features))) or 1.0
            scale_w = float(np.max(np.abs(projection_weights))) or 1.0

            q_feat = np.clip(np.round(features * (127.0 / scale_f)), -128, 127).astype(np.int8)
            q_w = np.clip(np.round(projection_weights * (127.0 / scale_w)), -128, 127).astype(np.int8)

            accum = q_feat.astype(np.int32) @ q_w.astype(np.int32)
            dequant = accum.astype(np.float32) * ((scale_f * scale_w) / (127.0 * 127.0))

            return dequant, {"strategy": "int8_quantized_projection", "path_class": "BOUNDED_APPROXIMATION"}

        return features @ projection_weights, {"strategy": "dense_fp32", "path_class": "EXACT"}
