"""
hyper/integrations/blender/HyperBlender/modes.py
================================================
Defines execution modes for HyperBlender:
- HYPER_INTERACTIVE_MODE: Optimized for viewport responsiveness, smooth 60 FPS,
  and perceptual reconstruction during navigation and editing.
- HYPER_FINAL_MODE: Optimized for final production render output, strict visual thresholds,
  mathematical convergence, and deterministic artifact-free image delivery.
"""

from dataclasses import dataclass


@dataclass
class HyperBlenderModeConfig:
    mode_name: str
    target_fps: int
    allow_perceptual_reconstruction: bool
    psnr_threshold_db: float
    ssim_threshold: float
    temporal_accumulation_weight: float
    bilateral_filter_enabled: bool
    deterministic_export: bool


INTERACTIVE_MODE = HyperBlenderModeConfig(
    mode_name="HYPER_INTERACTIVE_MODE",
    target_fps=60,
    allow_perceptual_reconstruction=True,
    psnr_threshold_db=32.0,
    ssim_threshold=0.95,
    temporal_accumulation_weight=0.90,
    bilateral_filter_enabled=True,
    deterministic_export=False,
)

FINAL_MODE = HyperBlenderModeConfig(
    mode_name="HYPER_FINAL_MODE",
    target_fps=24,
    allow_perceptual_reconstruction=False,
    psnr_threshold_db=45.0,
    ssim_threshold=0.99,
    temporal_accumulation_weight=0.0,  # Zero temporal blur in final mode
    bilateral_filter_enabled=False,
    deterministic_export=True,
)
