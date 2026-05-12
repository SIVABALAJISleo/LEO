import numpy as np

class TemporalReuseEngine:
    """
    Implements Temporal Reuse System (Section 17).
    Reuses previous frame computations or motion vectors to avoid full inference.
    """
    def __init__(self, tolerance=0.05):
        self.tolerance = tolerance
        self.previous_frame = None
        self.previous_compute_state = None
        
    def process_frame(self, current_frame, heavy_compute_fn):
        """
        If current_frame is sufficiently similar to previous_frame,
        reuse the previous_compute_state.
        """
        if self.previous_frame is not None:
            delta = np.mean(np.abs(current_frame - self.previous_frame))
            if delta < self.tolerance:
                return self.previous_compute_state, "SPARSE_REUSE"
                
        state = heavy_compute_fn(current_frame)
        self.previous_frame = current_frame
        self.previous_compute_state = state
        return state, "HEAVY_COMPUTE"
