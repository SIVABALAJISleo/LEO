"""
hyper_x/contract_miner.py
=============================================================================
HYPER-X: Autonomous Contract Miner
=============================================================================
Automatically analyzes input workloads to extract non-negotiable invariants:
  1. Numerical tolerances (epsilon, relative Frobenius norm bound).
  2. Perceptual thresholds (SSIM, PSNR, LPIPS for vision/graphics).
  3. Distributional bounds (Top-p divergence, perplexity match for language).
  4. Latency SLOs (max milliseconds) and 15W TDP power limits.
"""

from typing import Dict, Any, Optional
import numpy as np
from dataclasses import dataclass, field

@dataclass
class WorkloadContract:
    domain: str                           # "matrix", "language", "graphics", "simulation"
    tolerance_epsilon: float = 1e-3
    min_quality_score: float = 0.95
    min_ssim: float = 0.92
    min_psnr: float = 28.0
    max_latency_ms: float = 100.0
    max_power_watts: float = 15.0
    strict_exact_required: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

class ContractMiner:
    """Mines invariant constraints and quality contracts directly from workload metadata."""

    @staticmethod
    def mine_contract(workload_type: str, input_data: Any, user_hints: Optional[Dict[str, Any]] = None) -> WorkloadContract:
        hints = user_hints or {}

        if workload_type in ("matrix", "gemm", "tensor"):
            is_exact = hints.get("exact", False)
            eps = 0.0 if is_exact else hints.get("epsilon", 1e-3)
            return WorkloadContract(
                domain="matrix",
                tolerance_epsilon=eps,
                min_quality_score=1.0 if is_exact else 0.98,
                max_latency_ms=hints.get("max_latency_ms", 50.0),
                strict_exact_required=is_exact,
                metadata={"tensor_shape": getattr(input_data, "shape", None)}
            )

        elif workload_type in ("language", "nlp", "llm"):
            return WorkloadContract(
                domain="language",
                tolerance_epsilon=hints.get("epsilon", 0.05),
                min_quality_score=hints.get("min_quality", 0.95),
                max_latency_ms=hints.get("max_latency_ms", 250.0),
                strict_exact_required=False,
                metadata={"prompt_length": len(str(input_data))}
            )

        elif workload_type in ("graphics", "rendering", "vision"):
            return WorkloadContract(
                domain="graphics",
                min_ssim=hints.get("min_ssim", 0.92),
                min_psnr=hints.get("min_psnr", 28.0),
                max_latency_ms=hints.get("max_latency_ms", 16.67), # 60 FPS target SLO
                strict_exact_required=False,
                metadata={"resolution": getattr(input_data, "shape", None)}
            )

        else: # Generic scientific simulation
            return WorkloadContract(
                domain="simulation",
                tolerance_epsilon=hints.get("epsilon", 1e-4),
                min_quality_score=0.99,
                max_latency_ms=hints.get("max_latency_ms", 100.0),
                strict_exact_required=False,
                metadata={"input_type": type(input_data).__name__}
            )
