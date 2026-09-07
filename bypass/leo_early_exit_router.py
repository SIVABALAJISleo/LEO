import numpy as np
import logging
from typing import Tuple, Optional

logger = logging.getLogger(__name__)

class EarlyExitRouter:
    """
    Layer 2: Calibrated Confidence Early-Exit Router.
    Evaluates intermediate feature representations using Shannon entropy
    and top-1/top-2 logit margin to decide if early exit is mathematically justified.
    """
    def __init__(self, confidence_threshold: float = 0.90, max_entropy: float = 0.35):
        self.threshold = confidence_threshold
        self.max_entropy = max_entropy
        self.exit_count = 0
        self.pass_count = 0

    def evaluate_intermediate_state(
        self,
        hidden_tensor: np.ndarray,
        projection_head: Optional[np.ndarray] = None
    ) -> Tuple[bool, Optional[np.ndarray]]:
        """
        Takes intermediate activation tensor.
        Evaluates prediction entropy and confidence margin.
        Returns: (exit_early: bool, early_output: Optional[np.ndarray])
        """
        flat = hidden_tensor.reshape(-1)
        if flat.size == 0:
            return False, None
            
        # Numerical stable softmax over feature slice
        slice_len = min(256, flat.size)
        x = flat[:slice_len]
        x_max = np.max(x)
        exp_x = np.exp(x - x_max)
        probs = exp_x / np.maximum(1e-7, np.sum(exp_x))
        
        # 1. Top-1 vs Top-2 Margin Confidence
        sorted_probs = np.sort(probs)[::-1]
        top1 = float(sorted_probs[0])
        top2 = float(sorted_probs[1]) if len(sorted_probs) > 1 else 0.0
        margin_conf = top1 - top2
        
        # 2. Shannon Entropy: H(p) = -sum(p * log2(p))
        safe_p = np.clip(probs, 1e-12, 1.0)
        entropy = float(-np.sum(safe_p * np.log2(safe_p)) / np.log2(float(slice_len)))
        
        # Early exit condition: low uncertainty and high confidence margin
        is_confident = (top1 >= self.threshold or margin_conf >= 0.80) and (entropy <= self.max_entropy)
        
        if is_confident:
            self.exit_count += 1
            logger.debug(f"[EarlyExitRouter] Calibrated confidence={top1:.3f}, entropy={entropy:.3f}. Early exit granted.")
            # Project early representation
            if projection_head is not None and projection_head.shape[0] == flat.shape[0]:
                early_out = np.dot(flat, projection_head)
            else:
                early_out = flat[:slice_len].copy()
            return True, early_out
            
        self.pass_count += 1
        return False, None

    def get_stats(self) -> dict:
        total = self.exit_count + self.pass_count
        return {
            "exit_count": self.exit_count,
            "pass_count": self.pass_count,
            "early_exit_ratio_pct": round((self.exit_count / max(1, total)) * 100.0, 2)
        }

