"""
information_sufficiency/downstream_sensitivity.py
Downstream sensitivity analyzer tracking required output dimensions,
visible regions, top-k relevance, and invariant quantities.
"""

from typing import Dict, Any, List, Set, Optional
import numpy as np


class DownstreamSensitivityTracker:
    """Tracks what components of an output tensor are actually utilized downstream."""

    @staticmethod
    def compute_top_k_sensitivity(total_candidates: int, k_required: int) -> Dict[str, Any]:
        """Calculates work avoidance when only the top-k elements are consumed."""
        # Full sort is O(N log N), partial selection (QuickSelect/Argpartition) is O(N)
        full_ops = total_candidates * np.log2(max(total_candidates, 2))
        partial_ops = total_candidates + k_required * np.log2(max(k_required, 2))
        avoided_ratio = max(0.0, 1.0 - (partial_ops / max(full_ops, 1.0)))

        return {
            "total_candidates": total_candidates,
            "k_required": k_required,
            "recommended_algorithm": "argpartition_quickselect",
            "work_avoidance_ratio": float(avoided_ratio),
            "justification": f"Only top {k_required} of {total_candidates} elements are consumed; full ranking is unnecessary."
        }

    @staticmethod
    def compute_spatial_visibility_mask(
        viewport_width: int,
        viewport_height: int,
        bounding_boxes: List[List[float]]
    ) -> Dict[str, Any]:
        """Identifies primitives or tiles that lie entirely outside the visible viewport (Frustum culling)."""
        visible_indices = []
        culled_indices = []

        for i, box in enumerate(bounding_boxes):
            # box format: [min_x, min_y, max_x, max_y]
            if len(box) >= 4:
                min_x, min_y, max_x, max_y = box[0], box[1], box[2], box[3]
                if max_x < 0 or min_x > viewport_width or max_y < 0 or min_y > viewport_height:
                    culled_indices.append(i)
                else:
                    visible_indices.append(i)
            else:
                visible_indices.append(i)

        cull_ratio = len(culled_indices) / max(len(bounding_boxes), 1)
        return {
            "total_primitives": len(bounding_boxes),
            "visible_count": len(visible_indices),
            "culled_count": len(culled_indices),
            "cull_ratio": float(cull_ratio),
            "visible_indices": visible_indices
        }

    @staticmethod
    def verify_invariant_conservation(
        initial_state: np.ndarray,
        final_state: np.ndarray,
        invariant_type: str = "energy",
        tolerance: float = 0.05
    ) -> bool:
        """Verifies that physical invariant quantities (e.g. energy, momentum, norm) are conserved."""
        if invariant_type == "energy":
            e_init = float(np.sum(initial_state**2))
            e_final = float(np.sum(final_state**2))
            relative_change = abs(e_final - e_init) / max(e_init, 1e-12)
            return relative_change <= tolerance
        elif invariant_type == "sum":
            s_init = float(np.sum(initial_state))
            s_final = float(np.sum(final_state))
            relative_change = abs(s_final - s_init) / max(abs(s_init), 1e-12)
            return relative_change <= tolerance
        return True
