"""
hyper_x/leaf/observable.py
==========================
Observable Extractor Specification for LEAF Engine.

Philosophy:
    "Don't compute the ocean if the application only needs one drop."

An Observable defines the exact subset or transformation of the mathematical
state that the downstream application consumes.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
import numpy as np


class ObservableType(str, Enum):
    FULL_TENSOR = "FULL_TENSOR"
    SUB_SLICE = "SUB_SLICE"
    TOP_K = "TOP_K"
    ARGMAX = "ARGMAX"
    SCALAR_REDUCTION = "SCALAR_REDUCTION"
    SAMPLE_POINTS = "SAMPLE_POINTS"
    PERCEPTUAL_PROJECTION = "PERCEPTUAL_PROJECTION"


@dataclass(frozen=True)
class ObservableSpec:
    """Specification of what the application observes."""
    obs_type: ObservableType
    slice_indices: Optional[Tuple[slice, ...]] = None
    k: Optional[int] = None
    reduction_op: Optional[str] = None  # "sum", "mean", "norm", "max"
    sample_coordinates: Optional[np.ndarray] = None  # (N, D) coordinates

    def extract(self, full_state: np.ndarray) -> np.ndarray:
        """Extracts the observable from the full mathematical state."""
        if self.obs_type == ObservableType.FULL_TENSOR:
            return full_state

        if self.obs_type == ObservableType.SUB_SLICE:
            if self.slice_indices is None:
                return full_state
            return full_state[self.slice_indices]

        if self.obs_type == ObservableType.TOP_K:
            k = self.k or 5
            flat = full_state.flatten()
            if k >= len(flat):
                return flat
            topk_idx = np.argpartition(flat, -k)[-k:]
            return flat[topk_idx]

        if self.obs_type == ObservableType.ARGMAX:
            return np.array([np.argmax(full_state)], dtype=np.int64)

        if self.obs_type == ObservableType.SCALAR_REDUCTION:
            if self.reduction_op == "sum":
                return np.array([np.sum(full_state)], dtype=full_state.dtype)
            elif self.reduction_op == "mean":
                return np.array([np.mean(full_state)], dtype=full_state.dtype)
            elif self.reduction_op == "norm":
                return np.array([np.linalg.norm(full_state)], dtype=full_state.dtype)
            elif self.reduction_op == "max":
                return np.array([np.max(full_state)], dtype=full_state.dtype)
            return np.array([np.sum(full_state)], dtype=full_state.dtype)

        if self.obs_type == ObservableType.SAMPLE_POINTS:
            if self.sample_coordinates is None:
                return full_state
            # Query point coordinates
            coords = self.sample_coordinates
            values = []
            for c in coords:
                idx = tuple(int(round(x)) for x in c)
                values.append(full_state[idx])
            return np.array(values, dtype=full_state.dtype)

        return full_state
