"""
hyper/information/info_analyzer.py
==================================
Information-Requirement Analyzer:
Asks: "What information does the final application output actually depend upon?"
Identifies necessary vs redundant, recoverable, reusable, and predictable information.
"""

from typing import Dict, Any, List
import numpy as np


class InformationRequirementAnalyzer:
    """
    Evaluates informational bounds and minimal sufficient state representation.
    """
    def __init__(self):
        pass

    def evaluate_information_content(self, tensor: np.ndarray, tolerance_eps: float = 0.01) -> Dict[str, Any]:
        """
        Determines the minimal degree-of-freedom representation required.
        """
        total_elements = tensor.size
        
        # Spectral energy truncation
        if tensor.ndim == 2 and min(tensor.shape) > 2:
            s = np.linalg.svd(tensor[:64, :64], compute_uv=False) if min(tensor.shape) >= 64 else np.linalg.svd(tensor, compute_uv=False)
            total_energy = float(np.sum(s ** 2))
            cumulative_energy = np.cumsum(s ** 2) / max(1e-12, total_energy)
            k_necessary = int(np.searchsorted(cumulative_energy, 1.0 - (tolerance_eps ** 2))) + 1
            info_retention_ratio = round(k_necessary / len(s), 4)
        else:
            info_retention_ratio = 1.0

        necessary_elements = int(total_elements * info_retention_ratio)
        redundant_elements = total_elements - necessary_elements
        unnecessary_info_pct = round((redundant_elements / max(1, total_elements)) * 100.0, 2)

        return {
            "total_elements": total_elements,
            "necessary_elements": necessary_elements,
            "redundant_elements": redundant_elements,
            "unnecessary_info_pct": unnecessary_info_pct,
            "info_retention_ratio": info_retention_ratio,
        }
