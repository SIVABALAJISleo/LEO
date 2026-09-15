"""
hyper_x/leaf/implicit/query.py
==============================
Batch query and coordinate indexing engine for implicit fields.
"""

from typing import Any, Dict, List, Optional
import numpy as np

from .field import ImplicitField


class ImplicitQueryEngine:
    """Orchestrates fast batch queries on implicit fields."""

    def batch_query(self, field: ImplicitField, coordinates: np.ndarray) -> np.ndarray:
        return field.query(coordinates)

    def slice_query(self, field: ImplicitField, dim_slices: List[slice]) -> np.ndarray:
        """Evaluates slice bounds directly from implicit field parameters."""
        # For fields that support direct slice evaluation
        coords = np.array([[s.start or 0, s.stop or 10] for s in dim_slices])
        return field.query(coords)
