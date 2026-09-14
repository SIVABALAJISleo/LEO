"""
core_ai/attention/__init__.py
Attention mechanisms for LEO: Local Attention and Vectorized Block Attention.
"""

from .local_attention import (
    VectorizedBlockAttention,
    LocalAttention,
    LocalBlockAttentionModule,
    BlockAttentionResult,
)
from .token_merging import TokenMerger, FastContextIndex
from .speculative_orchestrator import SpeculativeOrchestrator
from .fused_attention import fused_attention_online_softmax, HeterogeneousDispatcher

__all__ = [
    "VectorizedBlockAttention",
    "LocalAttention",
    "LocalBlockAttentionModule",
    "BlockAttentionResult",
    "TokenMerger",
    "FastContextIndex",
    "SpeculativeOrchestrator",
    "fused_attention_online_softmax",
    "HeterogeneousDispatcher",
]
