"""
hyper/cache/contract_cache.py
=============================
Contract-Aware Content-Addressed Cache.
Only returns cached entries if the stored contract dominates the current requested contract.
Supports Cold-Start, Warm-Start, and Cache-Contamination benchmarks.
"""

import time
import hashlib
from typing import Dict, Any, Optional, Tuple
import numpy as np
from hyper.contracts.contract_types import UniversalContract


class ContractAwareCache:
    """
    Cache holding outputs tagged with the exact execution contract they satisfied.
    """
    def __init__(self, max_memory_mb: float = 2048.0):
        self._entries: Dict[str, Tuple[Any, UniversalContract, float]] = {}
        self.is_enabled: bool = True
        self.max_memory_mb = max_memory_mb
        self.hits = 0
        self.misses = 0

    def query(self, cache_key: str, required_contract: UniversalContract) -> Tuple[Optional[Any], bool]:
        """
        Retrieves cached value if present AND stored contract dominates required_contract.
        """
        if not self.is_enabled:
            return None, False

        entry = self._entries.get(cache_key)
        if entry is None:
            self.misses += 1
            return None, False

        result, stored_contract, timestamp = entry
        if stored_contract.dominates(required_contract):
            self.hits += 1
            return result, True
        
        # Stored result exists but does NOT meet the tighter contract requirement
        self.misses += 1
        return None, False

    def insert(self, cache_key: str, result: Any, contract: UniversalContract) -> None:
        if not self.is_enabled:
            return
        self._entries[cache_key] = (result, contract, time.time())

    def clear(self) -> None:
        self._entries.clear()
        self.hits = 0
        self.misses = 0
