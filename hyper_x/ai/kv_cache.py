#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
hyper_x/ai/kv_cache.py
======================
Total GPU Omega: Paged KV-Cache & Prefix Reuse Engine.

Eliminates redundant key-value tensor computation across multi-turn queries,
system prompts, and shared document prefixes.
"""

from __future__ import annotations
import hashlib
from typing import Dict, Any, Tuple, Optional, List
import numpy as np


class PagedKVCache:
    """Manages paged Key-Value attention caches with cryptographic prefix matching."""

    def __init__(self, page_size: int = 16):
        self.page_size = page_size
        self.cache_pages: Dict[str, Tuple[np.ndarray, np.ndarray]] = {}  # hash -> (K, V)
        self.total_tokens_cached: int = 0
        self.tokens_reused: int = 0

    def compute_prefix_hash(self, token_ids: List[int]) -> str:
        s = ",".join(str(t) for t in token_ids)
        return hashlib.sha256(s.encode("utf-8")).hexdigest()

    def lookup_prefix(
        self,
        token_ids: List[int]
    ) -> Tuple[int, Optional[Tuple[np.ndarray, np.ndarray]]]:
        """
        Finds the longest cached prefix matching the query tokens.
        Returns: (matched_length, (K, V))
        """
        best_len = 0
        best_kv = None

        # Check page boundaries (multiples of page_size down to 1 page)
        max_pages = len(token_ids) // self.page_size
        for num_pages in range(max_pages, 0, -1):
            end_idx = num_pages * self.page_size
            h = self.compute_prefix_hash(token_ids[:end_idx])
            if h in self.cache_pages:
                best_len = end_idx
                best_kv = self.cache_pages[h]
                self.tokens_reused += best_len
                break

        return best_len, best_kv

    def store_prefix(
        self,
        token_ids: List[int],
        K: np.ndarray,
        V: np.ndarray
    ):
        """Stores computed KV representations indexed by token sequence hash."""
        h = self.compute_prefix_hash(token_ids)
        self.cache_pages[h] = (K, V)
        self.total_tokens_cached += len(token_ids)
