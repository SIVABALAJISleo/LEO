"""
hyper_x/leaf/neural/surrogate.py
================================
Neural surrogate wrapper with fail-closed contract enforcement.
"""

from typing import Any, Callable, Dict, List, Optional, Tuple
import numpy as np

from .implicit_field import NeuralImplicitField
from ..contract import LeafContract, ContractTier


class NeuralSurrogate:
    """Wraps an implicit neural surrogate with fallback to exact computation."""

    def __init__(
        self,
        field: NeuralImplicitField,
        contract: LeafContract,
        reference_fallback: Callable[[np.ndarray], np.ndarray],
    ):
        self.field = field
        self.contract = contract
        self.reference_fallback = reference_fallback

    def evaluate(self, coordinates: np.ndarray) -> Tuple[np.ndarray, Dict[str, Any]]:
        """Evaluates neural surrogate; if contract check fails, falls back to reference."""
        pred = self.field.query_numpy(coordinates)

        # In non-exact / perceptual contracts, return prediction
        if self.contract.tier in (ContractTier.PERCEPTUAL_APPROXIMATION, ContractTier.PREDICTIVE):
            return pred, {"source": "NIR_SURROGATE", "fallback_used": False}

        # In strict contracts, spot-check sample
        sample_idx = [0, len(coordinates) - 1]
        sample_coords = coordinates[sample_idx]
        ref_sample = self.reference_fallback(sample_coords)
        pred_sample = pred[sample_idx]

        max_err = float(np.max(np.abs(pred_sample - ref_sample)))
        if max_err > self.contract.max_absolute_error:
            # Trigger fail-closed fallback
            exact_res = self.reference_fallback(coordinates)
            return exact_res, {
                "source": "EXACT_FALLBACK",
                "fallback_used": True,
                "spot_check_error": max_err,
            }

        return pred, {"source": "NIR_SURROGATE_VERIFIED", "fallback_used": False}
