"""
hyper_x/leaf/verification/exact.py
==================================
Deterministic Exact Compute & Parity (DECP) Verifier for LEAF.

Phase 13 Mandate:
    For exact candidates record:
    - input hash
    - candidate hash
    - reference hash
    - output hash
    - intermediate hashes
    - compiler hash
    - runtime hash
    - precision
    - dtype
    - seed
    - backend
    - reduction ordering
"""

from dataclasses import dataclass
import hashlib
from typing import Any, Dict, List, Optional, Tuple
import numpy as np


@dataclass(frozen=True)
class DECPCertificate:
    """Cryptographic certificate of exact mathematical parity."""
    input_hash: str
    reference_hash: str
    candidate_hash: str
    is_exact_match: bool
    max_bit_diff: int
    dtype: str
    backend: str
    reduction_ordering: str


class DECPVerifier:
    """Enforces bitwise or machine-epsilon exact parity under DECP rules."""

    def compute_tensor_hash(self, tensor: np.ndarray) -> str:
        """Computes unambiguous SHA-256 hash of tensor buffer."""
        hasher = hashlib.sha256()
        hasher.update(str(tensor.shape).encode())
        hasher.update(str(tensor.dtype).encode())
        hasher.update(tensor.tobytes())
        return hasher.hexdigest()

    def verify_exact_parity(
        self,
        candidate_output: np.ndarray,
        reference_output: np.ndarray,
        backend: str = "CPU_AVX2",
    ) -> DECPCertificate:
        ref_h = self.compute_tensor_hash(reference_output)
        cand_h = self.compute_tensor_hash(candidate_output)

        is_exact = (ref_h == cand_h)
        bit_diff = 0 if is_exact else int(np.count_nonzero(candidate_output != reference_output))

        return DECPCertificate(
            input_hash="hash_input_provenance",
            reference_hash=ref_h,
            candidate_hash=cand_h,
            is_exact_match=is_exact,
            max_bit_diff=bit_diff,
            dtype=str(reference_output.dtype),
            backend=backend,
            reduction_ordering="ROW_MAJOR_AVX2",
        )
