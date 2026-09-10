"""
hyper_x/wormhole_compiler/observable_compiler.py
=============================================================================
Universal Observable Compiler & ObservableIR (Section 3)
=============================================================================
Compiles application output definitions into an explicit ObservableIR,
distinguishing:
  - internal state (scratch buffers, unobserved activations)
  - intermediate state (unobserved products, temporary feature maps)
  - externally observable state (visible pixels, selected tokens, queried rows)

Rule:
Only optimize away an operation when it is proven not to affect the required
observable under the declared contract.
"""

from __future__ import annotations
import enum
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple, Callable, Set
import numpy as np


class ObservableDomain(str, enum.Enum):
    DENSE_TENSOR = "DENSE_TENSOR"
    GRAPHICS_PIXELS = "GRAPHICS_PIXELS"
    AI_TOKENS = "AI_TOKENS"
    DATABASE_ROWS = "DATABASE_ROWS"
    SCIENTIFIC_QUANTITY = "SCIENTIFIC_QUANTITY"
    VIDEO_FRAMES = "VIDEO_FRAMES"
    DISCRETE_DECISION = "DISCRETE_DECISION"


@dataclass
class ObservableIR:
    """
    Formal representation of the exact required observable.
    """
    observable_id: str
    domain: ObservableDomain
    description: str
    target_shape: Tuple[int, ...]
    dtype: str
    dimension_reduction_ratio: float  # |Observable| / |IntermediateState|
    tolerance: float = 0.0

    # Visibility & sensitivity masks
    is_decision_relevant_only: bool = False
    is_user_visible_only: bool = True
    mask_indices: Optional[List[int]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "observable_id": self.observable_id,
            "domain": self.domain.value,
            "description": self.description,
            "target_shape": self.target_shape,
            "dtype": self.dtype,
            "dimension_reduction_ratio": round(self.dimension_reduction_ratio, 6),
            "tolerance": self.tolerance,
            "is_decision_relevant_only": self.is_decision_relevant_only,
            "is_user_visible_only": self.is_user_visible_only,
        }


class UniversalObservableCompiler:
    """
    Constructs ObservableIR across AI, Graphics, Database, Scientific, and Tensor domains.
    """

    @staticmethod
    def full_tensor(shape: Tuple[int, ...], dtype: str = "float32", tolerance: float = 0.0) -> ObservableIR:
        """Full materialization required."""
        return ObservableIR(
            observable_id="OBS_FULL_TENSOR",
            domain=ObservableDomain.DENSE_TENSOR,
            description="Full dense tensor materialization",
            target_shape=shape,
            dtype=dtype,
            dimension_reduction_ratio=1.0,
            tolerance=tolerance,
            is_decision_relevant_only=False,
            is_user_visible_only=True,
        )

    @staticmethod
    def output_projection(output_dim: int, total_dim: int, tolerance: float = 1e-4) -> ObservableIR:
        """Only linear projection or vector product is observed (e.g. y = (A @ B) @ x)."""
        return ObservableIR(
            observable_id="OBS_OUTPUT_PROJECTION",
            domain=ObservableDomain.DENSE_TENSOR,
            description=f"Linear output projection of dimension {output_dim} from total {total_dim}",
            target_shape=(output_dim, 1),
            dtype="float32",
            dimension_reduction_ratio=float(output_dim) / max(1.0, float(total_dim)),
            tolerance=tolerance,
            is_decision_relevant_only=True,
            is_user_visible_only=False,
        )

    @staticmethod
    def graphics_visible_pixels(
        resolution: Tuple[int, int],
        channels: int = 3,
        occluded_mask: Optional[np.ndarray] = None,
        min_ssim: float = 0.92
    ) -> ObservableIR:
        """Graphics domain: visible pixels within viewport frustum."""
        H, W = resolution
        reduction = 1.0
        if occluded_mask is not None:
            visible_ratio = float(np.mean(~occluded_mask))
            reduction = max(0.01, visible_ratio)

        return ObservableIR(
            observable_id="OBS_GRAPHICS_VISIBLE_PIXELS",
            domain=ObservableDomain.GRAPHICS_PIXELS,
            description=f"Visible screen-space pixels at {W}x{H} resolution",
            target_shape=(H, W, channels),
            dtype="float32",
            dimension_reduction_ratio=reduction,
            tolerance=1.0 - min_ssim,
            is_decision_relevant_only=False,
            is_user_visible_only=True,
        )

    @staticmethod
    def ai_requested_tokens(
        vocab_size: int,
        top_k: int = 1,
        mode: str = "ARGMAX"
    ) -> ObservableIR:
        """AI domain: only argmax token ID or Top-K logits are observed by downstream sampler."""
        reduction = float(top_k) / max(1.0, float(vocab_size))
        return ObservableIR(
            observable_id=f"OBS_AI_{mode}_{top_k}",
            domain=ObservableDomain.AI_TOKENS,
            description=f"AI inference observable: {mode} (top-{top_k}) over vocabulary size {vocab_size}",
            target_shape=(top_k,),
            dtype="int64" if mode == "ARGMAX" else "float32",
            dimension_reduction_ratio=reduction,
            tolerance=0.0,
            is_decision_relevant_only=True,
            is_user_visible_only=True,
        )

    @staticmethod
    def database_queried_rows(
        total_rows: int,
        returned_limit: int,
        columns: int
    ) -> ObservableIR:
        """Database domain: only filtered and limited rows are returned to the client."""
        reduction = float(min(returned_limit, total_rows)) / max(1.0, float(total_rows))
        return ObservableIR(
            observable_id=f"OBS_DB_LIMIT_{returned_limit}",
            domain=ObservableDomain.DATABASE_ROWS,
            description=f"Database query result: top {returned_limit} of {total_rows} rows",
            target_shape=(min(returned_limit, total_rows), columns),
            dtype="mixed",
            dimension_reduction_ratio=reduction,
            tolerance=0.0,
            is_decision_relevant_only=True,
            is_user_visible_only=True,
        )

    @staticmethod
    def scientific_physical_observable(
        field_shape: Tuple[int, ...],
        conserved_quantities: List[str],
        tolerance: float = 1e-6
    ) -> ObservableIR:
        """Scientific computing: integrated macroscopic quantity or sensor measurement."""
        return ObservableIR(
            observable_id="OBS_SCIENTIFIC_QUANTITY",
            domain=ObservableDomain.SCIENTIFIC_QUANTITY,
            description=f"Macroscopic quantities: {', '.join(conserved_quantities)}",
            target_shape=(len(conserved_quantities),),
            dtype="float64",
            dimension_reduction_ratio=1.0 / max(1.0, float(np.prod(field_shape))),
            tolerance=tolerance,
            is_decision_relevant_only=True,
            is_user_visible_only=True,
        )
