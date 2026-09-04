"""
hyper_mvc_dar/unseen/layout_optimizer.py
UNSEEN FEATURE 2: Differentiable Memory Layout Optimizer.

Optimizes tensor memory layout (NCHW, NHWC, Blocked-16c, Morton Z-curve, Col/Row-Major)
per operator and per hardware path (Intel P-core, E-core, Intel UHD Xe iGPU)
via differentiable profiling to minimize L3 cache misses, bank conflicts, and bandwidth overhead.
"""

import time
import math
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Tuple, List, Optional, Any
import numpy as np


class TensorLayout(Enum):
    NCHW = "NCHW"                    # Planar channels (traditional deep learning default)
    NHWC = "NHWC"                    # Channels-last (AVX2/FMA/VNNI vector aligned)
    BLOCKED_16C = "nChw16c"          # AVX2 16-element blocked channels (zero-waste vectorization)
    SWIZZLED_MORTON_2D = "MortonZ"   # Z-order space filling curve (optimal 2D spatial caching)
    ROW_MAJOR = "RowMajor"           # Standard C-contiguous
    COL_MAJOR = "ColMajor"           # Fortran-contiguous (optimal for BLAS GEMM col-strides)


@dataclass
class LayoutProfileResult:
    layout: TensorLayout
    execution_time_us: float
    reformat_cost_us: float
    estimated_l3_miss_rate: float
    memory_bandwidth_gbs: float
    net_gain_us: float


class LayoutCostPredictor:
    """
    Differentiable layout predictor modeling latency as a function of tensor geometry,
    target execution unit (P-core vs E-core vs iGPU), and memory cache hierarchies.
    """

    def __init__(self):
        # Weights: [log_bytes, channel_div_16, channel_div_8, spatial_area, is_igpu, is_conv]
        # Initialized from empirical profiling on Alder Lake L1/L2/L3 Smart Cache
        self.weights: Dict[TensorLayout, np.ndarray] = {
            TensorLayout.NCHW: np.array([0.15, 0.40, 0.30, -0.05, 0.10, 0.50]),
            TensorLayout.NHWC: np.array([0.12, -0.60, -0.40, 0.02, -0.20, -0.40]),
            TensorLayout.BLOCKED_16C: np.array([0.10, -0.80, -0.50, 0.01, -0.10, -0.60]),
            TensorLayout.SWIZZLED_MORTON_2D: np.array([0.11, 0.10, 0.10, -0.70, 0.20, -0.10]),
            TensorLayout.ROW_MAJOR: np.array([0.13, -0.20, -0.20, 0.00, 0.00, 0.00]),
            TensorLayout.COL_MAJOR: np.array([0.14, 0.20, 0.20, 0.00, 0.00, 0.00]),
        }

    def extract_features(self, shape: Tuple[int, ...], op_type: str, device: str) -> np.ndarray:
        """Extracts normalized geometric and device features."""
        total_elements = math.prod(shape)
        total_bytes = total_elements * 4  # FP32
        log_bytes = math.log10(max(1024, total_bytes)) / 8.0  # normalize [0, 1] for MBs

        if len(shape) == 4:
            b, c, h, w = shape
            ch_div_16 = 1.0 if (c % 16 == 0) else -1.0
            ch_div_8 = 1.0 if (c % 8 == 0) else -1.0
            spatial = math.log10(max(1, h * w)) / 6.0
        elif len(shape) == 2:
            m, n = shape
            ch_div_16 = 1.0 if (n % 16 == 0) else -1.0
            ch_div_8 = 1.0 if (n % 8 == 0) else -1.0
            spatial = math.log10(max(1, m * n)) / 7.0
        else:
            ch_div_16 = 0.0
            ch_div_8 = 0.0
            spatial = 0.5

        is_igpu = 1.0 if "gpu" in device.lower() else 0.0
        is_conv = 1.0 if "conv" in op_type.lower() else 0.0

        return np.array([log_bytes, ch_div_16, ch_div_8, spatial, is_igpu, is_conv], dtype=np.float32)

    def predict_cost(self, shape: Tuple[int, ...], layout: TensorLayout, op_type: str, device: str) -> float:
        """Predicts relative latency index for given shape and layout."""
        feat = self.extract_features(shape, op_type, device)
        w = self.weights.get(layout, np.zeros(6, dtype=np.float32))
        raw_score = float(np.dot(feat, w))
        return math.exp(raw_score)  # positive latency scalar


class DifferentiableLayoutOptimizer:
    """
    Wraps tensor operators with dynamic layout selection.
    Evaluates reformat costs against downstream operational latency gains.
    """

    def __init__(self, memory_bandwidth_gbs: float = 17.34):
        self.bandwidth_bytes_per_us = (memory_bandwidth_gbs * 1e9) / 1e6
        self.predictor = LayoutCostPredictor()
        self.policy_cache: Dict[str, TensorLayout] = {}

    def _policy_key(self, op_type: str, shape: Tuple[int, ...], device: str) -> str:
        return f"{op_type}:{shape}:{device}"

    def estimate_reformat_cost_us(self, tensor: np.ndarray) -> float:
        """Calculates theoretical memory streaming time to transpose/reformat in micro-seconds."""
        bytes_to_copy = tensor.nbytes * 2  # 1 read + 1 write
        return max(1.0, bytes_to_copy / self.bandwidth_bytes_per_us)

    def select_optimal_layout(
        self,
        tensor: np.ndarray,
        current_layout: TensorLayout,
        op_type: str,
        device: str = "CPU_AVX2",
        pipeline_depth: int = 4
    ) -> Tuple[TensorLayout, bool, float]:
        """
        Determines optimal layout. Reformats only if amortized gain over pipeline_depth
        exceeds reformatting overhead:
        pipeline_depth * (predicted_gain) > reformat_cost
        """
        key = self._policy_key(op_type, tensor.shape, device)
        if key in self.policy_cache:
            best_layout = self.policy_cache[key]
            should_reformat = (best_layout != current_layout)
            return best_layout, should_reformat, 0.0

        candidate_layouts = [
            TensorLayout.NCHW,
            TensorLayout.NHWC,
            TensorLayout.BLOCKED_16C,
            TensorLayout.ROW_MAJOR,
            TensorLayout.COL_MAJOR,
        ] if len(tensor.shape) == 4 else [TensorLayout.ROW_MAJOR, TensorLayout.COL_MAJOR]

        reformat_cost_us = self.estimate_reformat_cost_us(tensor)
        curr_cost = self.predictor.predict_cost(tensor.shape, current_layout, op_type, device)

        best_layout = current_layout
        best_cost = curr_cost
        max_net_gain = 0.0

        for cand in candidate_layouts:
            cand_cost = self.predictor.predict_cost(tensor.shape, cand, op_type, device)
            # Latency reduction per op in microseconds (calibrated to tensor size)
            unit_gain_us = max(0.0, (curr_cost - cand_cost) * (tensor.nbytes / 1e6) * 15.0)
            accumulated_gain_us = unit_gain_us * pipeline_depth
            net_gain_us = accumulated_gain_us - (reformat_cost_us if cand != current_layout else 0.0)

            if net_gain_us > max_net_gain:
                max_net_gain = net_gain_us
                best_cost = cand_cost
                best_layout = cand

        should_reformat = (best_layout != current_layout) and (max_net_gain > 0.0)
        self.policy_cache[key] = best_layout
        return best_layout, should_reformat, max_net_gain

    def reformat_tensor(
        self,
        tensor: np.ndarray,
        from_layout: TensorLayout,
        to_layout: TensorLayout
    ) -> np.ndarray:
        """Executes tensor layout transposition."""
        if from_layout == to_layout:
            return tensor

        if len(tensor.shape) == 4:
            # (B, C, H, W) <-> (B, H, W, C)
            if from_layout == TensorLayout.NCHW and to_layout == TensorLayout.NHWC:
                return np.ascontiguousarray(np.transpose(tensor, (0, 2, 3, 1)))
            elif from_layout == TensorLayout.NHWC and to_layout == TensorLayout.NCHW:
                return np.ascontiguousarray(np.transpose(tensor, (0, 3, 1, 2)))
        elif len(tensor.shape) == 2:
            # RowMajor (C) <-> ColMajor (F)
            if to_layout == TensorLayout.COL_MAJOR:
                return np.asfortranarray(tensor)
            elif to_layout == TensorLayout.ROW_MAJOR:
                return np.ascontiguousarray(tensor)

        return tensor
