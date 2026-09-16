"""
hyper/integrations/blender/HyperBlender/verifier/render_verifier.py
"""
import numpy as np
from hyper.verification import VerificationEngine

class BlenderRenderVerifier:
    """Verifies output image correctness against strict mode thresholds."""
    def verify_viewport_frame(self, actual: np.ndarray, reference: np.ndarray, mode_config) -> bool:
        if mode_config.mode_name == "HYPER_FINAL_MODE":
            # Exact or high PSNR required
            metrics = VerificationEngine.verify_image(actual, reference)
            return bool(metrics["psnr"] >= mode_config.psnr_threshold_db and metrics["ssim"] >= mode_config.ssim_threshold)
        else:
            # Interactive mode requires perceptual pass
            metrics = VerificationEngine.verify_image(actual, reference)
            return bool(metrics["psnr"] >= mode_config.psnr_threshold_db)
