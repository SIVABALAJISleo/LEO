"""
hyper_x/leaf/verification/contract.py
====================================
Contract satisfaction verifier for LEAF.
"""

from typing import Any, Dict, List, Optional, Tuple
import numpy as np

from ..contract import LeafContract, ContractTier


class ContractVerifier:
    """Verifies candidate execution under explicit contract bounds."""

    def verify(
        self,
        candidate_output: np.ndarray,
        reference_output: np.ndarray,
        contract: LeafContract,
    ) -> Tuple[bool, float, str]:
        return contract.validate(candidate_output, reference_output)
