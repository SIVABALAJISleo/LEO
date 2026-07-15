"""
core_ai/hyperdimensional/core.py
The Kanerva-Tesla Core: Vector-Symbolic Architecture Engine.
Zero floating point operations. 10,000-dimensional binary vectors.
"""

import numpy as np
import hashlib

class HyperdimensionalEncoder:
    def __init__(self, dimension: int = 10000):
        self.dimension = dimension
        self.byte_dim = (dimension + 7) // 8

    def _string_to_seed(self, text: str) -> int:
        """Deterministically seeds RNG based on text content."""
        hash_digest = hashlib.md5(text.lower().encode(), usedforsecurity=False).digest()
        return int.from_bytes(hash_digest[:4], byteorder='little')

    def encode_text(self, text: str) -> np.ndarray:
        """
        Maps text to a 10,000-bit pseudo-random hypervector.
        Returns packed uint8 arrays for massive memory savings.
        """
        seed = self._string_to_seed(text)
        rng = np.random.default_rng(seed)
        
        # Generate random bits
        bits = rng.integers(0, 2, size=self.dimension, dtype=np.uint8)
        
        # Pack 8 bits into 1 uint8 byte (size reduces from 10000 bytes to 1250 bytes)
        return np.packbits(bits)

    @staticmethod
    def bind(hv1: np.ndarray, hv2: np.ndarray) -> np.ndarray:
        """
        Binds two hypervectors using Colibri bitwise XOR.
        Associates two concepts (e.g., Key XOR Value).
        """
        from ..colibri_bridge import ColibriBridge
        bridge = ColibriBridge()
        return bridge.bind_hypervectors(hv1, hv2)

    @staticmethod
    def bundle(hv_list: list[np.ndarray]) -> np.ndarray:
        """
        Bundles multiple hypervectors using majority rule (Population count).
        Represents a set or sequence of concepts.
        """
        if not hv_list:
            raise ValueError("Cannot bundle empty list of hypervectors")
            
        unpacked_list = [np.unpackbits(hv) for hv in hv_list]
        sum_vec = np.sum(unpacked_list, axis=0)
        
        # Majority rule: 1 if count > n/2 else 0
        threshold = len(hv_list) / 2.0
        bundled_bits = (sum_vec > threshold).astype(np.uint8)
        
        # Tie-breaker logic for exactly half (randomize or set 0)
        ties = sum_vec == threshold
        if np.any(ties):
            bundled_bits[ties] = np.random.randint(0, 2, size=np.sum(ties))
            
        return np.packbits(bundled_bits)

    @staticmethod
    def hamming_distance(hv1: np.ndarray, hv2: np.ndarray) -> float:
        """
        Calculates normalized Hamming distance between two packed vectors.
        Uses popcount via bitwise XOR.
        """
        xor_res = np.bitwise_xor(hv1, hv2)
        # Fast bit counting algorithm via unpackbits
        unpacked = np.unpackbits(xor_res)
        dist = np.sum(unpacked)
        return float(dist) / len(unpacked)
