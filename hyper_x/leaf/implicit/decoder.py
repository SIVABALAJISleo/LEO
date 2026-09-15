"""
hyper_x/leaf/implicit/decoder.py
================================
Evaluates queries and reconstructs discrete states from implicit fields.
"""

from typing import Any, Dict, List, Optional, Tuple
import numpy as np

from .field import ImplicitField


class ImplicitDecoder:
    """Decodes coordinates from implicit field representations."""

    def decode_points(self, field: ImplicitField, points: np.ndarray) -> np.ndarray:
        return field.query(points)

    def decode_grid(
        self,
        field: ImplicitField,
        x_range: Tuple[float, float, int],
        y_range: Optional[Tuple[float, float, int]] = None,
    ) -> np.ndarray:
        """Decodes an entire 1D or 2D discrete grid from continuous field."""
        if y_range is None:
            xs = np.linspace(x_range[0], x_range[1], x_range[2], dtype=np.float32)
            return field.query(xs)
        else:
            xs = np.linspace(x_range[0], x_range[1], x_range[2], dtype=np.float32)
            ys = np.linspace(y_range[0], y_range[1], y_range[2], dtype=np.float32)
            grid_x, grid_y = np.meshgrid(xs, ys)
            coords = np.stack([grid_x.ravel(), grid_y.ravel()], axis=1)
            vals = field.query(coords)
            return vals.reshape((y_range[2], x_range[2]))
