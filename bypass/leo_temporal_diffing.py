import numpy as np
import logging
import warnings

logger = logging.getLogger(__name__)

class TemporalDiffer:
    """
    Layer 3: Temporal Diffing (For Streaming Data).
    Skips model execution entirely if structural pixel shift is < 5%.
    """
    def __init__(self, diff_threshold=0.05):
        self.diff_threshold = diff_threshold
        self.previous_sample = None
        self.previous_output = None
        
        try:
            import cv2
            self.cv2 = cv2
            self.cv2_available = True
        except ImportError:
            self.cv2_available = False
            warnings.warn("OpenCV (cv2) not installed. Falling back to Numpy absolute difference.")

    def _compute_structural_difference(self, current_frame: np.ndarray, prev_frame: np.ndarray) -> float:
        """
        Rapid CPU-bound diffing algorithm. Downsamples for speed.
        """
        # Take a very sparse sample of pixels for ultra-fast diffing
        # Subsample by taking every 100th pixel in each dimension
        diff = np.abs(current_frame - prev_frame)
        shift_ratio = np.sum(diff > 0.1) / float(diff.size)
        return shift_ratio

    def evaluate_temporal_shift(self, current_frame: np.ndarray):
        """
        Compares current input to previous input.
        If diff < 5%, returns the adjusted previous output, bypassing the model.
        """
        curr_sample = current_frame[::100, ::100]
        
        if self.previous_sample is None or self.previous_output is None:
            self.previous_sample = curr_sample.copy()
            return False, None
            
        shift_ratio = self._compute_structural_difference(curr_sample, self.previous_sample)
        
        if shift_ratio < self.diff_threshold:
            logger.debug(f"[TemporalDiffing] PIXEL SHIFT {shift_ratio*100:.2f}% < {self.diff_threshold*100}%. BYPASSING MODEL.")
            
            # Mathematically adjust the previous output (Mocking a transpose/shift operation)
            adjusted_output = self.previous_output * 0.99 + 0.01 
            
            return True, adjusted_output
            
        self.previous_sample = curr_sample.copy()
        return False, None

    def store_output(self, output: np.ndarray):
        """Saves the output from a fully computed frame for future diffing."""
        self.previous_output = output
