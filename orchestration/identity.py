import hashlib
from typing import Tuple

class IdentityMapper:
    """
    Module I: HIGH-SPEED IDENTITY MAPPING
    - O(1) representation conversion.
    - Minimal branching.
    """
    @staticmethod
    def map_to_bits(text: str) -> Tuple[int, bytes]:
        """
        Converts raw text to a unique 16-bit index and a 32-byte hash tag.
        """
        # Lowercase and strip (Minimal normalization)
        clean = text.lower().strip().encode()
        
        # BLAKE2b is extremely fast on modern CPUs
        h = hashlib.blake2b(clean, digest_size=32).digest()
        
        # Index: First 2 bytes (16-bit space)
        idx = (h[0] << 8) | h[1]
        
        # Tag: Bytes 2-6 (For collision validation)
        tag = h[2:6]
        
        return idx, tag
