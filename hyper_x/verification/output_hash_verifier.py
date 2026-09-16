"""
hyper_x/verification/output_hash_verifier.py
============================================
Phase 1: Output Hash Verifier.
Validates SHA-256 cryptographic hashes between candidate and isolated reference outputs.
Fail-closed default: passed = False.
"""

from __future__ import annotations
import hashlib
import json
from dataclasses import dataclass
from typing import Any
import numpy as np


@dataclass
class OutputHashVerificationResult:
    passed: bool = False  # Fail-closed default
    candidate_hash: str = ""
    reference_hash: str = ""
    is_match: bool = False


class OutputHashVerifier:
    """
    Computes cryptographic digests of outputs and validates hash equality.
    """

    @staticmethod
    def hash_output(output: Any) -> str:
        if isinstance(output, np.ndarray):
            raw = np.ascontiguousarray(output).tobytes()
        elif isinstance(output, (bytes, bytearray)):
            raw = bytes(output)
        elif isinstance(output, str):
            raw = output.encode("utf-8")
        else:
            raw = json.dumps(str(output), sort_keys=True).encode("utf-8")
        return hashlib.sha256(raw).hexdigest()

    @classmethod
    def verify(cls, candidate_output: Any, expected_reference_hash: str) -> OutputHashVerificationResult:
        c_hash = cls.hash_output(candidate_output)
        is_match = (c_hash == expected_reference_hash)
        return OutputHashVerificationResult(
            passed=is_match,
            candidate_hash=c_hash,
            reference_hash=expected_reference_hash,
            is_match=is_match,
        )
