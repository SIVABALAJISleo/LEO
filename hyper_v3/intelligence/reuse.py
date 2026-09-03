"""
hyper_v3/intelligence/reuse.py
Discovers operand reuse, common subexpressions, and cache residency matches.
"""

from typing import Dict, Any, List, Optional
import hashlib
import json
import numpy as np


class ReuseAnalyzer:
    """Computes operand fingerprints and discovers subexpression reuse."""

    @staticmethod
    def compute_tensor_signature(tensor: np.ndarray) -> str:
        if not isinstance(tensor, np.ndarray):
            return hashlib.sha256(str(tensor).encode("utf-8")).hexdigest()
        summary = {
            "shape": list(tensor.shape),
            "dtype": str(tensor.dtype),
            "sample_corners": [
                float(tensor.ravel()[0]) if tensor.size > 0 else 0.0,
                float(tensor.ravel()[-1]) if tensor.size > 0 else 0.0,
                float(np.mean(tensor)) if tensor.size > 0 else 0.0
            ]
        }
        return hashlib.sha256(json.dumps(summary, sort_keys=True).encode("utf-8")).hexdigest()

    @staticmethod
    def match_prefix_tokens(query_tokens: List[int], cached_keys: List[List[int]]) -> Optional[int]:
        max_prefix_len = 0
        best_match_idx = None
        for i, key in enumerate(cached_keys):
            match_len = 0
            for a, b in zip(query_tokens, key):
                if a == b:
                    match_len += 1
                else:
                    break
            if match_len > max_prefix_len:
                max_prefix_len = match_len
                best_match_idx = i
        return best_match_idx
