"""
hyper_cel/prediction/predictor.py
=============================================================================
HYPER-CEL: Cheap Predictive Surrogates
=============================================================================
Provides ultra-fast, cheap initial approximations:
  1. LowRankPredictor: Rank-r matrix factor approximation (O(M*r*N) vs O(M*K*N)).
  2. KANPredictor: B-spline lookup-table approximation for non-linear layers.
  3. SpeculativeDraftPredictor: Multi-token drafting for language generation.
"""

import time
import numpy as np
from typing import Dict, Any, Tuple, List, Optional
from core_ai.alchemy_kan_ffn import AlchemyKANFFNLayer

class LowRankPredictor:
    """
    Predicts matrix multiplication Y_hat = A @ B using randomized rank-r SVD projection.
    Complexity: O((M+N)*r*K) << O(M*K*N) when r << min(M, K, N).
    """

    def __init__(self, rank: int = 16):
        self.rank = rank

    def predict(self, A: np.ndarray, B: np.ndarray) -> Tuple[np.ndarray, Dict[str, Any]]:
        t0 = time.perf_counter()
        M, K = A.shape
        _, N = B.shape
        r = min(self.rank, M, K, N)

        # Randomized Gaussian test matrix for range finder
        Omega = np.random.randn(K, r).astype(np.float32)
        Y_sample = A @ Omega # (M, r)
        Q, _ = np.linalg.qr(Y_sample) # (M, r) orthonormal basis

        # Project B onto low-rank basis
        # A @ B ~= Q @ (Q.T @ A @ B)
        # Group as (Q @ (Q.T @ A)) @ B or Q @ ((Q.T @ A) @ B)
        B_proj = (Q.T @ A) @ B # (r, N)
        Y_hat = Q @ B_proj # (M, N)

        t1 = time.perf_counter()
        latency_ms = (t1 - t0) * 1000.0

        # Reference FLOPs: 2 * M * K * N
        # Low-rank FLOPs: 2*M*K*r + 2*M*r^2 + 2*r*K*N + 2*M*r*N
        ref_flops = 2.0 * M * K * N
        actual_flops = (2.0 * M * K * r) + (2.0 * r * K * N) + (2.0 * M * r * N)
        cer = 1.0 - (actual_flops / max(1.0, ref_flops))

        return Y_hat, {
            "predictor": "LOW_RANK_SVD",
            "rank": r,
            "latency_ms": round(latency_ms, 3),
            "ref_flops": ref_flops,
            "actual_flops": actual_flops,
            "cer": round(cer, 4)
        }

class KANSplinePredictor:
    """
    Predicts non-linear transformations using fast 1024-sample LUT B-splines.
    """

    def __init__(self, d_model: int = 128, d_hidden: int = 256):
        self.layer = AlchemyKANFFNLayer(d_model=d_model, d_hidden=d_hidden, use_lut=True)

    def predict(self, x: np.ndarray) -> Tuple[np.ndarray, Dict[str, Any]]:
        return self.layer.forward(x)

class SpeculativeDraftPredictor:
    """
    Predicts multi-token future candidates (1..K draft tokens) using tiny predictor.
    """

    def __init__(self, draft_len: int = 4):
        self.draft_len = draft_len

    def draft_tokens(self, context_ids: List[int], tiny_model_logits_fn) -> Tuple[List[int], float]:
        t0 = time.perf_counter()
        draft = []
        curr = list(context_ids)
        for _ in range(self.draft_len):
            logits = tiny_model_logits_fn(curr)
            next_token = int(np.argmax(logits))
            draft.append(next_token)
            curr.append(next_token)
        t1 = time.perf_counter()
        return draft, (t1 - t0) * 1000.0
