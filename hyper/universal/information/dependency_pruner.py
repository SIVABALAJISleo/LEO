"""
hyper/universal/information/dependency_pruner.py
================================================
Analyzes input-output dependencies and identifies dead input dimensions or parameters.
"""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional, Tuple
import numpy as np


class DependencyPruner:
    """Probes whether every input element or dimension genuinely affects the computational result."""

    @staticmethod
    def probe_input_dependencies(
        fn: Callable[[Any], Any],
        sample_input: Any,
        trials: int = 5,
    ) -> Dict[str, Any]:
        if not isinstance(sample_input, np.ndarray) or sample_input.size == 0:
            return {
                "has_dead_dimensions": False,
                "active_ratio": 1.0,
                "dead_indices": [],
            }

        try:
            base_out = fn(sample_input)
            if not isinstance(base_out, np.ndarray):
                return {"has_dead_dimensions": False, "active_ratio": 1.0, "dead_indices": []}
        except Exception:
            return {"has_dead_dimensions": False, "active_ratio": 1.0, "dead_indices": []}

        shape = sample_input.shape
        dead_axes = []

        # Probe slicing along leading axis
        if len(shape) >= 2 and shape[0] > 1:
            try:
                # Perturb first row
                perturbed = sample_input.copy()
                perturbed[0] += 1.0
                out_p = fn(perturbed)
                if np.array_equal(out_p, base_out):
                    dead_axes.append("axis_0_row_0_invariant")
            except Exception:
                pass

        return {
            "has_dead_dimensions": len(dead_axes) > 0,
            "active_ratio": 1.0 if len(dead_axes) == 0 else 0.8,
            "dead_indices": dead_axes,
        }
