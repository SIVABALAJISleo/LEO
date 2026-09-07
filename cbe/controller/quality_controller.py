"""
cbe/controller/quality_controller.py
Real-time visual quality supervisor enforcing the RenderingContract.
Triggers Quality-First Emergency Mode whenever visual artifacts exceed tolerance bounds.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any, List


@dataclass
class QualityContract:
    target_fps: float = 60.0
    target_resolution: str = "1920x1080"
    min_ssim: float = 0.950
    min_psnr: float = 30.0
    max_latency_ms: float = 16.67
    max_ghosting_coeff: float = 0.05
    max_temporal_flicker: float = 0.03
    max_power_watts: float = 35.0


class QualityController:
    """
    Supervises render output quality against declared contracts.
    Decisively shuts off aggressive bypasses if temporal artifacts or blurring violate contracts.
    """
    def __init__(self, contract: Optional[QualityContract] = None):
        self.contract = contract if contract is not None else QualityContract()
        self.emergency_mode_active = False
        self.emergency_cooldown_frames = 0
        self.ssim_history: List[float] = []
        self.psnr_history: List[float] = []

    def evaluate_quality(
        self,
        current_ssim: float,
        current_psnr: float,
        ghosting_score: float = 0.0,
        flicker_score: float = 0.0
    ) -> Dict[str, Any]:
        """
        Evaluates visual metrics against contract and toggles emergency mode if violated.
        """
        self.ssim_history.append(current_ssim)
        self.psnr_history.append(current_psnr)
        
        contract_violated = (
            current_ssim < self.contract.min_ssim
            or current_psnr < self.contract.min_psnr
            or ghosting_score > self.contract.max_ghosting_coeff
            or flicker_score > self.contract.max_temporal_flicker
        )
        
        if contract_violated:
            self.emergency_mode_active = True
            self.emergency_cooldown_frames = 15  # Force 15 frames of safe computation
            action = "ACTIVATE_QUALITY_EMERGENCY"
        elif self.emergency_cooldown_frames > 0:
            self.emergency_cooldown_frames -= 1
            action = f"EMERGENCY_RECOVERY ({self.emergency_cooldown_frames} frames left)"
        else:
            self.emergency_mode_active = False
            action = "CONTRACT_SATISFIED"

        return {
            "action": action,
            "emergency_mode": self.emergency_mode_active,
            "current_ssim": current_ssim,
            "min_ssim": self.contract.min_ssim,
            "current_psnr": current_psnr,
            "ghosting_score": ghosting_score,
            "contract_passed": not contract_violated,
        }

    def get_adjustment_directives(self) -> Dict[str, Any]:
        """Returns directives for schedulers and renderers."""
        if self.emergency_mode_active:
            return {
                "force_native_resolution": True,
                "disable_temporal_extrapolation": True,
                "disable_frame_prediction": True,
                "increase_fresh_render_pct": 0.50,
                "enable_strong_clamping": True,
            }
        return {
            "force_native_resolution": False,
            "disable_temporal_extrapolation": False,
            "disable_frame_prediction": False,
            "increase_fresh_render_pct": 0.0,
            "enable_strong_clamping": True,
        }
