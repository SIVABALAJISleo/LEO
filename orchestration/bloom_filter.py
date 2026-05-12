import hashlib
from typing import List

class SemanticBloomFilter:
    """
    Module BF: SEMANTIC BLOOM FILTER
    - Prevents invalid CDN requests (404-avoidance).
    - Lightweight bitset representation.
    """
    def __init__(self, size: int = 10000, hash_count: int = 3):
        self.size = size
        self.hash_count = hash_count
        self.bitset = 0 # Using a large integer as a bitset

    def _get_hashes(self, item: str) -> List[int]:
        hashes = []
        for i in range(self.hash_count):
            # Salted SHA256 hashes
            h = hashlib.sha256(f"{i}:{item}".encode()).hexdigest()
            hashes.append(int(h, 16) % self.size)
        return hashes

    def add(self, item: str):
        for h in self._get_hashes(item):
            self.bitset |= (1 << h)

    def check(self, item: str) -> bool:
        for h in self._get_hashes(item):
            if not (self.bitset & (1 << h)):
                return False
        return True

    def export_state(self) -> str:
        # Export as hex for CDN deployment
        return hex(self.bitset)

    def import_state(self, hex_val: str):
        self.bitset = int(hex_val, 16)
