"""
hyper/temporal/temporal_engine.py
=================================
Temporal Coherence Engine:
- Detects inter-frame & inter-step static regions
- Computes only new_information + residual_information
- Evaluates temporal reuse ratio
"""

import time
import numpy as np
from typing import Dict, Any, Tuple, Optional


class TemporalComputationEngine:
    """
    Exploits inter-frame temporal coherence in physical simulations and graphics.
    """
    def __init__(self, change_threshold: float = 0.01):
        self.change_threshold = change_threshold
        self.previous_state: Optional[np.ndarray] = None

    def process_step(self, current_state: np.ndarray) -> Tuple[np.ndarray, Dict[str, Any]]:
        t0 = time.perf_counter()
        if self.previous_state is None or self.previous_state.shape != current_state.shape:
            self.previous_state = current_state.copy()
            return current_state, {
                "is_full_compute": True,
                "temporal_reuse_pct": 0.0,
                "cer": 0.0,
                "elapsed_ms": round((time.perf_counter() - t0) * 1000.0, 3)
            }

        delta = current_state - self.previous_state
        changed_mask = np.abs(delta) > self.change_threshold
        changed_elements = int(np.sum(changed_mask))
        total_elements = current_state.size

        reuse_pct = round((1.0 - (changed_elements / max(1, total_elements))) * 100.0, 2)
        cer = round(reuse_pct / 100.0, 4)

        # Reconstruct updated state
        reconstructed = self.previous_state.copy()
        reconstructed[changed_mask] = current_state[changed_mask]
        self.previous_state = reconstructed.copy()

        t_elapsed_ms = (time.perf_counter() - t0) * 1000.0
        return reconstructed, {
            "is_full_compute": False,
            "changed_elements": changed_elements,
            "temporal_reuse_pct": reuse_pct,
            "cer": cer,
            "elapsed_ms": round(t_elapsed_ms, 3)
        }
