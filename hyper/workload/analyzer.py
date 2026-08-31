"""
hyper/workload/analyzer.py
==========================
Workload Analyzer extracting static and dynamic properties:
- operation graph
- dependency flow
- critical path
- sparse / low-rank / compressible / predictable regions
- temporal & spatial coherence
"""

import numpy as np
from typing import Dict, Any, List, Optional
from .graph import OpNode, ComputationGraph


class WorkloadAnalyzer:
    """
    Analyzes computational workloads and extracts machine-readable structural profiles.
    """
    def __init__(self):
        pass

    def analyze_tensor_workload(self, name: str, A: np.ndarray, B: Optional[np.ndarray] = None) -> Dict[str, Any]:
        """
        Extracts structural sparsity, spectral rank, compressibility, and flop requirements.
        """
        M, K = A.shape if A.ndim == 2 else (A.shape[0], 1)
        N = B.shape[1] if (B is not None and B.ndim == 2) else 1

        baseline_flops = 2 * M * K * N if B is not None else 2 * M * K

        # Sparsity detection
        zero_count = int(np.sum(A == 0))
        total_elements = A.size
        sparsity_pct = round((zero_count / max(1, total_elements)) * 100.0, 2)

        # Spectral rank proxy
        approx_rank = min(M, K)
        if A.ndim == 2 and min(M, K) > 4:
            s_sample = min(32, min(M, K))
            s = np.linalg.svd(A[:s_sample, :s_sample], compute_uv=False)
            effective_rank = int(np.sum(s > 0.05 * s[0]))
            approx_rank = max(1, int(effective_rank * (min(M, K) / s_sample)))

        rank_ratio = round(approx_rank / max(1, min(M, K)), 3)

        # Compressibility estimate (Shannon entropy on 8-bit quantized sample)
        q_sample = np.clip((A[:32, :32] if A.ndim == 2 else A[:64]) * 127.0, -128, 127).astype(np.int8)
        _, counts = np.unique(q_sample, return_counts=True)
        probs = counts / counts.sum()
        entropy = float(-np.sum(probs * np.log2(probs + 1e-12)))
        compressibility_pct = round(max(0.0, (1.0 - (entropy / 8.0)) * 100.0), 2)

        return {
            "workload_name": name,
            "shape_A": list(A.shape),
            "shape_B": list(B.shape) if B is not None else None,
            "baseline_flops": baseline_flops,
            "sparsity_pct": sparsity_pct,
            "approx_rank": approx_rank,
            "rank_ratio": rank_ratio,
            "compressibility_pct": compressibility_pct,
            "is_sparse_candidate": sparsity_pct > 30.0,
            "is_low_rank_candidate": rank_ratio < 0.4,
            "is_compressible": compressibility_pct > 25.0,
        }
