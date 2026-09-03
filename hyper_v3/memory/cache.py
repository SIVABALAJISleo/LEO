"""
hyper_v3/memory/cache.py
4-Tier Cache Hierarchy (L1: Hot, L2: Intermediate, L3: Semantic Lattice, L4: Persistent Disk).
"""

from typing import Dict, Any, Optional
from collections import OrderedDict
import hashlib
import json
import numpy as np


class CacheHierarchy:
    """Manages L1 hot, L2 intermediate, L3 semantic, and L4 persistent caches."""

    def __init__(self, l1_cap: int = 128, l2_cap: int = 256, l3_cap: int = 512):
        self.l1_hot: OrderedDict[str, Any] = OrderedDict()
        self.l2_intermediate: OrderedDict[str, Any] = OrderedDict()
        self.l3_semantic: OrderedDict[str, Any] = OrderedDict()
        self.l1_cap = l1_cap
        self.l2_cap = l2_cap
        self.l3_cap = l3_cap

    def lookup(self, key_hash: str) -> Optional[Any]:
        # Check L1
        if key_hash in self.l1_hot:
            self.l1_hot.move_to_end(key_hash)
            return self.l1_hot[key_hash]
        # Check L2
        if key_hash in self.l2_intermediate:
            val = self.l2_intermediate[key_hash]
            self.put_l1(key_hash, val)
            return val
        # Check L3
        if key_hash in self.l3_semantic:
            val = self.l3_semantic[key_hash]
            self.put_l1(key_hash, val)
            return val
        return None

    def put_l1(self, key_hash: str, value: Any):
        if key_hash in self.l1_hot:
            self.l1_hot.move_to_end(key_hash)
        self.l1_hot[key_hash] = value
        if len(self.l1_hot) > self.l1_cap:
            old_k, old_v = self.l1_hot.popitem(last=False)
            self.put_l2(old_k, old_v)

    def put_l2(self, key_hash: str, value: Any):
        self.l2_intermediate[key_hash] = value
        if len(self.l2_intermediate) > self.l2_cap:
            self.l2_intermediate.popitem(last=False)

    def put_l3_semantic(self, key_hash: str, value: Any):
        self.l3_semantic[key_hash] = value
        if len(self.l3_semantic) > self.l3_cap:
            self.l3_semantic.popitem(last=False)
