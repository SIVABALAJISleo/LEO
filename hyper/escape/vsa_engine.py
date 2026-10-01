"""
hyper/escape/vsa_engine.py
==========================
Vector Symbolic Architecture (VSA) / Hyperdimensional Computing Engine.
Fulfills Section 29 of Master Specification.

Mandatory Constraints:
- VSA operates on binary hyperdimensional representations (D = 8,192 or 10,000 bits),
  using XOR binding, bundling (majority vote), cyclic permutation, and popcount distance.
- VSA is an ALGEBRAIC / SYMBOLIC computing substrate.
- VSA is NOT bitwise or IEEE-754 equivalent to continuous FP32 dense matrix computation.
- Strictly forbidden from replacing exact FP32 operations unless the workload has a formally
  declared VSA_SYMBOLIC_CONTRACT or APPROXIMATE_STATISTICAL_CONTRACT.
"""

from __future__ import annotations

import enum
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np


class VSAContractType(enum.Enum):
    EXACT_FP32 = "EXACT_FP32"
    EXACT_INTEGER = "EXACT_INTEGER"
    VSA_SYMBOLIC_ASSOCIATIVE = "VSA_SYMBOLIC_ASSOCIATIVE"
    VSA_HYPERDIMENSIONAL = "VSA_HYPERDIMENSIONAL"
    APPROXIMATE_STATISTICAL = "APPROXIMATE_STATISTICAL"


@dataclass
class VSAContract:
    contract_type: VSAContractType
    dimension_bits: int = 8192
    similarity_threshold: float = 0.85
    allow_symbolic_escape: bool = False


class VSAEngine:
    """
    Vector Symbolic Architecture (VSA) Engine.
    Provides sound hyperdimensional symbolic operations while strictly gating
    any conversion against formal semantic contracts.
    """

    def __init__(self, dimension_bits: int = 8192):
        self.dimension_bits = dimension_bits
        self.uint32_words = dimension_bits // 32

    def create_random_hypervector(self, seed: Optional[int] = None) -> np.ndarray:
        """Create a uniform random binary hypervector of size D bits (packed as uint32)."""
        rng = np.random.default_rng(seed)
        return rng.integers(0, 0xFFFFFFFF + 1, size=self.uint32_words, dtype=np.uint32)

    def bind(self, v1: np.ndarray, v2: np.ndarray) -> np.ndarray:
        """
        Binding operation: Bitwise XOR.
        Associative, commutative, invertible (v ^ v = 0).
        Preserves quasi-orthogonality.
        """
        return np.bitwise_xor(v1, v2)

    def unbind(self, bound: np.ndarray, v: np.ndarray) -> np.ndarray:
        """Unbinding is identical to binding under XOR: (A ^ B) ^ A = B."""
        return np.bitwise_xor(bound, v)

    def permute(self, v: np.ndarray, shifts: int = 1) -> np.ndarray:
        """
        Permutation operation: Cyclic bit-shift.
        Used to represent sequence ordering or positional syntax.
        """
        bits = np.unpackbits(v.view(np.uint8))[:self.dimension_bits]
        rotated = np.roll(bits, shifts)
        return np.packbits(rotated).view(np.uint32)

    def bundle(self, vectors: List[np.ndarray]) -> np.ndarray:
        """
        Bundling (Superposition) operation: Majority voting across vectors.
        Result is similar to all input vectors.
        """
        if not vectors:
            return np.zeros(self.uint32_words, dtype=np.uint32)
        if len(vectors) == 1:
            return vectors[0].copy()

        # Unpack to boolean arrays
        all_bits = [np.unpackbits(v.view(np.uint8))[:self.dimension_bits] for v in vectors]
        stacked = np.stack(all_bits, axis=0)  # Shape: (N, D)
        summed = np.sum(stacked, axis=0)
        majority = (summed > (len(vectors) / 2.0)).astype(np.uint8)
        return np.packbits(majority).view(np.uint32)

    def hamming_distance(self, v1: np.ndarray, v2: np.ndarray) -> int:
        """Calculate bitwise Hamming distance between two hypervectors."""
        diff = np.bitwise_xor(v1, v2)
        # Count bits across uint32 array
        # In Python/NumPy, unpackbits gives exact bit count
        return int(np.count_nonzero(np.unpackbits(diff.view(np.uint8))[:self.dimension_bits]))

    def cosine_similarity(self, v1: np.ndarray, v2: np.ndarray) -> float:
        """Normalized similarity in [-1.0, 1.0], where 1.0 is identical and 0.0 is orthogonal."""
        dist = self.hamming_distance(v1, v2)
        return 1.0 - 2.0 * (dist / float(self.dimension_bits))

    def evaluate_vsa_applicability(
        self,
        contract: VSAContract,
        workload_name: str = "generic_workload",
    ) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Strict Contract Truth Gate:
        Disallows VSA replacement for standard continuous FP32 tensor ops.
        Approves VSA only when contract is explicitly symbolic/associative.
        """
        if contract.contract_type in (VSAContractType.EXACT_FP32, VSAContractType.EXACT_INTEGER):
            return (
                False,
                "VSA_DISALLOWED_UNDER_EXACT_CONTRACT: VSA binary hypervector operations do not satisfy "
                "continuous IEEE-754 / bitwise numerical exactness.",
                {
                    "contract": contract.contract_type.value,
                    "status": "REJECTED_BY_TRUTH_GATE",
                    "reason": "Exactness contract violation",
                },
            )

        if contract.contract_type in (
            VSAContractType.VSA_SYMBOLIC_ASSOCIATIVE,
            VSAContractType.VSA_HYPERDIMENSIONAL,
        ) or (contract.contract_type == VSAContractType.APPROXIMATE_STATISTICAL and contract.allow_symbolic_escape):
            return (
                True,
                "VSA_PERMITTED: Workload contract formally establishes symbolic associative semantics.",
                {
                    "contract": contract.contract_type.value,
                    "status": "PROVEN_ESCAPE",
                    "dimension_bits": self.dimension_bits,
                    "simd_backend": "AVX2_POPCOUNT",
                },
            )

        return (
            False,
            f"VSA_UNSUPPORTED: Contract {contract.contract_type.value} does not permit VSA replacement.",
            {"contract": contract.contract_type.value, "status": "UNKNOWN"},
        )
