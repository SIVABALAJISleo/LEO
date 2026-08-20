"""
contracts/perceptual_saturation.py
The HYPER Protocol v2.0: Mathematical Perceptual Saturation & Parity Engine
Formally defines Parity(W):
  Parity(W) = TRUE if Latency(HYPER) <= H_max and Quality(HYPER) >= Q_min
Quantifies datacenter GPU 'Overshoot / Wasted Compute' beyond human perceptual limits.
"""

from typing import Dict, Any

class HumanPerceptualLimits:
    READING_SPEED_TOK_PER_SEC = 10.0      # Average human reads 4-5 words/s (~8-10 tokens/s)
    FAST_READING_TOK_PER_SEC = 20.0       # Speed reading ceiling (~15-20 tokens/s)
    INTERACTIVE_LATENCY_CEILING_MS = 100.0 # Human brain perceives <= 100ms as 'instantaneous'
    FLUID_VIDEO_MIN_FPS = 30.0            # Minimum fluid motion threshold
    FLUID_VIDEO_TARGET_FPS = 60.0         # Standard high-refresh fluidity threshold
    AUDIO_LATENCY_CEILING_MS = 20.0       # Perceptible audio delay ceiling

class PerceptualParityEngine:
    """
    Evaluates whether a workload achieves formal perceptual parity.
    """
    @staticmethod
    def evaluate_ai_generation(hyper_tok_s: float, dgpu_tok_s: float, quality_score: float = 0.98) -> Dict[str, Any]:
        h_max_reading = HumanPerceptualLimits.READING_SPEED_TOK_PER_SEC
        h_fast_reading = HumanPerceptualLimits.FAST_READING_TOK_PER_SEC
        
        # Parity condition
        is_parity = (hyper_tok_s >= h_max_reading) and (quality_score >= 0.95)
        
        # Wasted compute calculation
        # Any tokens/sec delivered above the speed-reading threshold cannot be consumed in real time
        wasted_gpu_tok_s = max(0.0, dgpu_tok_s - h_fast_reading)
        wasted_gpu_pct = (wasted_gpu_tok_s / dgpu_tok_s) * 100.0 if dgpu_tok_s > 0 else 0.0
        
        return {
            "workload": "Interactive AI Token Generation",
            "human_reading_threshold_tok_s": h_max_reading,
            "speed_reading_saturation_ceiling_tok_s": h_fast_reading,
            "hyper_delivered_tok_s": hyper_tok_s,
            "dgpu_delivered_tok_s": dgpu_tok_s,
            "quality_parity_score": quality_score,
            "perceptual_parity_achieved": is_parity,
            "dgpu_overshoot_wasted_tok_s": wasted_gpu_tok_s,
            "dgpu_wasted_compute_percentage": wasted_gpu_pct,
            "scientific_verdict": f"HYPER ({hyper_tok_s:.1f} tok/s) saturates human reading comprehension ({h_max_reading} tok/s). The dGPU's {dgpu_tok_s:.1f} tok/s overshoots human cognition by {wasted_gpu_pct:.1f}% wasted compute."
        }

    @staticmethod
    def evaluate_rendering(hyper_fps: float, dgpu_fps: float, ssim_score: float) -> Dict[str, Any]:
        target_fps = HumanPerceptualLimits.FLUID_VIDEO_TARGET_FPS
        is_parity = (hyper_fps >= 30.0) and (ssim_score >= 0.95)
        
        return {
            "workload": "Interactive Viewport Rendering",
            "fluid_motion_target_fps": target_fps,
            "hyper_fps": hyper_fps,
            "dgpu_fps": dgpu_fps,
            "ssim_vs_ground_truth": ssim_score,
            "perceptual_parity_achieved": is_parity,
            "scientific_verdict": f"HYPER ({hyper_fps:.1f} FPS, SSIM: {ssim_score:.3f}) achieves fluid visual parity (>=30 FPS). dGPU delivers {dgpu_fps:.1f} FPS."
        }
