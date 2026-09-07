"""
cbe/reconstruction/frame_reconstruction.py
Master multi-tier frame reconstruction pipeline.
Dynamically routes between temporal integration, neural super-resolution on Intel iGPU,
and Contrast-Adaptive Sharpening based on confidence and latency contracts.
"""

from __future__ import annotations

import numpy as np
from typing import Optional, Dict, Any, Tuple

from .temporal_reconstruction import TemporalSuperResolution
from .spatial_reconstruction import SpatialReconstructor
from .neural_reconstruction import NeuralReconstructor
from .confidence_map import ConfidenceMapCalculator


class FrameReconstructionPipeline:
    """
    Unified reconstructor selecting between:
    - Tier A: Temporal Super-Resolution (High history confidence)
    - Tier B: Neural Super-Resolution via Intel iGPU (Moderate confidence / complex edges)
    - Tier C: Spatial CAS Upscaling (Disoccluded / fallback)
    """
    def __init__(self, sharpness: float = 0.45, enable_neural: bool = True):
        self.tsr = TemporalSuperResolution(sharpness=sharpness)
        self.spatial = SpatialReconstructor(sharpness=sharpness)
        self.neural = NeuralReconstructor(enable_ov_gpu=True) if enable_neural else None
        self.confidence_calc = ConfidenceMapCalculator()

    def reconstruct_frame(
        self,
        low_res_frame: np.ndarray,
        target_height: int,
        target_width: int,
        motion_vectors: np.ndarray,
        current_depth: np.ndarray,
        prev_depth: np.ndarray,
        history_frame: Optional[np.ndarray] = None,
        reactive_mask: Optional[np.ndarray] = None,
        disocclusion_mask: Optional[np.ndarray] = None,
        prefer_neural: bool = False
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Executes optimal reconstruction pass and returns reconstructed frame + telemetry.
        """
        conf_map = self.confidence_calc.compute(
            current_depth=current_depth,
            reprojected_depth=prev_depth,
            motion_vectors=motion_vectors,
            reactive_mask=reactive_mask
        )
        avg_conf = float(np.mean(conf_map))
        
        # Route logic
        if prefer_neural and self.neural is not None and history_frame is not None:
            # Neural path on Intel UHD iGPU
            # Downsample inputs to match low_res scale for neural network
            H_lr, W_lr, _ = low_res_frame.shape
            mv_lr = motion_vectors[::max(1, target_height // H_lr), ::max(1, target_width // W_lr)][:H_lr, :W_lr]
            hist_lr = history_frame[::max(1, target_height // H_lr), ::max(1, target_width // W_lr)][:H_lr, :W_lr]
            
            reconstructed, backend, ms = self.neural.reconstruct(low_res_frame, hist_lr, mv_lr)
            method = f"NEURAL_RECONSTRUCTION_{backend}"
        elif history_frame is not None and avg_conf >= 0.70:
            # Temporal Super-Resolution
            reconstructed = self.tsr.reconstruct(
                low_res_color=low_res_frame,
                target_height=target_height,
                target_width=target_width,
                motion_vectors=motion_vectors,
                current_depth=current_depth,
                prev_depth=prev_depth,
                history_color=history_frame,
                reactive_mask=reactive_mask,
                disocclusion_mask=disocclusion_mask
            )
            method = "TEMPORAL_SUPER_RESOLUTION"
            ms = 1.2
        else:
            # Edge-directed spatial CAS upscaling
            reconstructed = self.spatial.upscale(low_res_frame, target_height, target_width)
            method = "SPATIAL_CAS_UPSCALING"
            ms = 0.5
            
        return reconstructed, {
            "method": method,
            "latency_ms": ms,
            "avg_confidence": round(avg_conf, 4),
            "target_resolution": f"{target_width}x{target_height}",
            "input_resolution": f"{low_res_frame.shape[1]}x{low_res_frame.shape[0]}"
        }
