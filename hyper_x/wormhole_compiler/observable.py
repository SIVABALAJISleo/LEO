"""
hyper_x/wormhole_compiler/observable.py
=============================================================================
HYPER-X Required Observables Compiler: Distinguishing Output from Intermediate State
=============================================================================
Identifies what information is strictly required to satisfy the application contract.
Prevents materializing massive intermediate tensor states when downstream observers
only require lower-dimensional projections, decision-relevant flags, or summaries.

Examples:
  - Full matrix vs Ax (Matrix-Vector associativity O(N^2) vs O(N^3))
  - Full database scan vs Top-K result
  - Full simulation field vs Threshold crossing event
  - Full rendering vs Visible pixels
  - Full probability distribution vs Argmax
"""

from __future__ import annotations
from typing import Dict, Any, Optional, Tuple, List, Callable
import numpy as np
from hyper_x.wormhole_compiler.schemas import ObservableRequirement


class ObservableCompiler:
    """Formal compiler and extractor for contract-required observables."""

    @staticmethod
    def full_matrix(M: int, N: int, tolerance: float = 1e-4) -> ObservableRequirement:
        """Application requires the full M x N output matrix."""
        return ObservableRequirement(
            observable_id="OBS_FULL_MATRIX",
            description="Full M x N dense matrix materialization",
            output_type="FULL_MATRIX",
            dimension_reduction_ratio=1.0,
            extractor_fn_name="extract_identity",
            tolerance=tolerance,
            is_decision_relevant_only=False,
            is_user_visible_only=True
        )

    @staticmethod
    def matrix_vector_projection(M: int, tolerance: float = 1e-4) -> ObservableRequirement:
        """Application only needs C @ x = (A @ B) @ x. Allows A @ (B @ x) in O(N^2)."""
        return ObservableRequirement(
            observable_id="OBS_MATRIX_VECTOR_PROJECTION",
            description="Matrix-vector product projection y = C @ x without materializing C",
            output_type="VECTOR",
            dimension_reduction_ratio=1.0 / max(1, M),
            extractor_fn_name="extract_vector_projection",
            tolerance=tolerance,
            is_decision_relevant_only=True,
            is_user_visible_only=False
        )

    @classmethod
    def vector_projection(cls, M: int, projection_dim: int = 1, tolerance: float = 1e-4) -> ObservableRequirement:
        """Alias for matrix_vector_projection."""
        return cls.matrix_vector_projection(M=M, tolerance=tolerance)

    @staticmethod
    def top_k(k: int, total_dim: int, tolerance: float = 1e-3) -> ObservableRequirement:
        """Application only requires indices and values of top-k outputs (e.g. beam search)."""
        return ObservableRequirement(
            observable_id=f"OBS_TOP_{k}",
            description=f"Top-{k} largest output values and indices out of {total_dim}",
            output_type="TOP_K",
            dimension_reduction_ratio=k / max(1, total_dim),
            extractor_fn_name="extract_top_k",
            tolerance=tolerance,
            is_decision_relevant_only=True,
            is_user_visible_only=True
        )

    @staticmethod
    def argmax(total_dim: int) -> ObservableRequirement:
        """Application only requires classification argmax index."""
        return ObservableRequirement(
            observable_id="OBS_ARGMAX",
            description=f"Argmax class label out of {total_dim} elements",
            output_type="ARGMAX",
            dimension_reduction_ratio=1.0 / max(1, total_dim),
            extractor_fn_name="extract_argmax",
            tolerance=0.0,
            is_decision_relevant_only=True,
            is_user_visible_only=True
        )

    @staticmethod
    def threshold_crossing(threshold_value: float) -> ObservableRequirement:
        """Application only needs detection of values exceeding threshold (e.g. collision, trigger)."""
        return ObservableRequirement(
            observable_id="OBS_THRESHOLD_CROSSING",
            description=f"Boolean mask and coordinates exceeding threshold {threshold_value}",
            output_type="THRESHOLD_BOOLEAN",
            dimension_reduction_ratio=0.05,
            extractor_fn_name="extract_threshold",
            tolerance=1e-4,
            is_decision_relevant_only=True,
            is_user_visible_only=False
        )

    @staticmethod
    def summary_statistic(stat_type: str = "mean_and_variance") -> ObservableRequirement:
        """Application only needs summary statistical moments."""
        return ObservableRequirement(
            observable_id=f"OBS_STATISTIC_{stat_type.upper()}",
            description=f"Sufficient statistics: {stat_type}",
            output_type="STATISTIC",
            dimension_reduction_ratio=0.001,
            extractor_fn_name="extract_statistic",
            tolerance=1e-3,
            is_decision_relevant_only=True,
            is_user_visible_only=True
        )

    @staticmethod
    def visible_pixels(viewport_mask: np.ndarray) -> ObservableRequirement:
        """Application only requires rendering within active camera/viewport bounds."""
        active_ratio = float(np.mean(viewport_mask))
        return ObservableRequirement(
            observable_id="OBS_VISIBLE_PIXELS",
            description=f"Visible screen region ({active_ratio*100:.1f}% of total domain)",
            output_type="PIXELS",
            dimension_reduction_ratio=active_ratio,
            extractor_fn_name="extract_visible_region",
            tolerance=1e-3,
            is_decision_relevant_only=False,
            is_user_visible_only=True
        )


class ObservableExtractor:
    """Extracts observables from raw tensor states."""

    @staticmethod
    def extract_top_k(tensor: np.ndarray, k: int = 10) -> Tuple[np.ndarray, np.ndarray]:
        flat = tensor.flatten()
        k_eff = min(k, len(flat))
        indices = np.argpartition(flat, -k_eff)[-k_eff:]
        sorted_sub = np.argsort(-flat[indices])
        sorted_indices = indices[sorted_sub]
        return flat[sorted_indices], sorted_indices

    @staticmethod
    def extract_argmax(tensor: np.ndarray) -> int:
        return int(np.argmax(tensor))

    @staticmethod
    def extract_threshold(tensor: np.ndarray, threshold: float) -> Tuple[np.ndarray, int]:
        mask = tensor > threshold
        return mask, int(np.sum(mask))

    @staticmethod
    def extract_vector_projection(A: np.ndarray, B: np.ndarray, x: np.ndarray) -> np.ndarray:
        """Evaluates y = A @ (B @ x) in O(M*K + K*N) flops without forming A @ B."""
        Bx = B @ x
        return A @ Bx
