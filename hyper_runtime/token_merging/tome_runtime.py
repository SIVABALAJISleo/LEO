#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
hyper_runtime/token_merging/tome_runtime.py
==========================================
Runtime interface for Token Merging (ToMe).
"""

from typing import List, Tuple, Dict, Any, Union
import numpy as np
from .tome_engine import TokenMergingEngine


class TokenMergingRuntime:
    """
    Runtime wrapper for ToMe sequence length reduction.
    """
    def __init__(self, merge_ratio: float = 0.25):
        self.engine = TokenMergingEngine(merge_ratio=merge_ratio)

    def merge_tokens(
        self,
        tokens: list,
        hidden_states: Union[np.ndarray, list] = None
    ) -> Tuple[list, Any, Dict[str, Any]]:
        if hidden_states is None:
            # Synthetic embedding fallback if only tokens are provided
            seq_len = len(tokens)
            rng = np.random.default_rng(len(tokens))
            hidden_states = rng.standard_normal((seq_len, 64)).astype(np.float32)
        elif isinstance(hidden_states, list):
            hidden_states = np.array(hidden_states, dtype=np.float32)

        return self.engine.merge_tokens(tokens, hidden_states)
