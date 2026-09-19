"""
backend/caoe/intent_router.py
=============================
CAOE Phase 3: Contract-Aware Intent Layer (IntentLayer_v2).

Transforms static rule-based query routing into Contract-Negotiated execution:
1. Classifies query/workload intent (e.g., GEMM, FFT, RENDERING, INFERENCE, GENERAL).
2. Infers application contract (tolerances, precision space, cache policy, SLA).
3. Routes execution through CAOE orchestrator.
4. Emits real-time telemetry and parity tracking.
"""

from __future__ import annotations

import dataclasses
import time
from typing import Any, Callable, Dict, List, Optional, Tuple

import numpy as np

from .caoe_engine import ContractAwareOptimizationEngine
from .contract_analyzer import Contract, WorkloadSpec


@dataclasses.dataclass
class IntentClassification:
    intent_type: str
    confidence: float
    parameters: Dict[str, Any] = dataclasses.field(default_factory=dict)


class IntentLayer_v2:
    """Contract-Aware Intent Routing & Execution Layer."""

    def __init__(self, caoe_engine: Optional[ContractAwareOptimizationEngine] = None) -> None:
        self.caoe = caoe_engine or ContractAwareOptimizationEngine()

    def classify_query(self, query: str) -> IntentClassification:
        """Classify incoming task query or signature into an operational intent."""
        q = query.lower()
        if any(k in q for k in ["render", "frame", "pixel", "shader", "scene", "ssim"]):
            return IntentClassification(
                intent_type="RENDERING",
                confidence=0.95,
                parameters={"perceptual_metric": "SSIM", "target_ssim": 0.99, "cache_ttl": 5.0},
            )
        elif any(k in q for k in ["token", "embedding", "llm", "inference", "prompt", "top_k"]):
            return IntentClassification(
                intent_type="INFERENCE",
                confidence=0.92,
                parameters={"functional_metric": "TOP_K", "k": 5, "cache_ttl": 60.0},
            )
        elif any(k in q for k in ["fft", "frequency", "fourier", "spectral"]):
            return IntentClassification(
                intent_type="FFT",
                confidence=0.98,
                parameters={"relative_error": 1e-10, "cache_ttl": 0.0},
            )
        elif any(k in q for k in ["matrix", "gemm", "matmul", "linear", "dot"]):
            return IntentClassification(
                intent_type="GEMM",
                confidence=0.90,
                parameters={"relative_error": 5e-3, "cache_ttl": 10.0},
            )
        else:
            return IntentClassification(
                intent_type="GENERAL",
                confidence=0.80,
                parameters={"relative_error": 1e-4, "cache_ttl": 0.0},
            )

    def infer_contract_from_intent(
        self,
        intent: IntentClassification,
        shape: Tuple[int, ...],
        name: str = "workload",
    ) -> Contract:
        """Infer contract specification from classified intent."""
        rel_tol = intent.parameters.get("relative_error", 1e-3)
        cache_ttl = intent.parameters.get("cache_ttl", 0.0)
        perceptual = intent.parameters.get("perceptual_metric")
        functional = intent.parameters.get("functional_metric")
        k = intent.parameters.get("k", 5)

        return Contract(
            name=name,
            input_shape=shape,
            output_type="float32",
            tolerance={
                "absolute_error": rel_tol,
                "relative_error": rel_tol,
                "perceptual_metric": 0.99 if perceptual else None,
                "functional_metric": 0.95 if functional else None,
            },
            precision_options=[32, 16, 8],
            precision=32,
            sparsity_tolerance=0.0,
            cache_ttl=cache_ttl,
            fallback="full_computation",
            perceptual_metric=perceptual,
            functional_metric=functional,
            k=k,
        )

    def route_and_execute(
        self,
        query: str,
        input_tensor: np.ndarray,
        computation_fn: Callable[[np.ndarray, int, float], np.ndarray],
        reference_execution: Optional[np.ndarray] = None,
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        End-to-end execution:
        1. Classify query.
        2. Infer contract.
        3. Optimize & execute via CAOE.
        """
        intent = self.classify_query(query)
        spec = WorkloadSpec(
            name=f"{intent.intent_type.lower()}_{query[:16]}",
            shape=input_tensor.shape,
            task_type=intent.intent_type,
            perceptual_metric=intent.parameters.get("perceptual_metric"),
            functional_metric=intent.parameters.get("functional_metric"),
            k=intent.parameters.get("k", 5),
        )

        result, meta = self.caoe.optimize_and_execute(
            workload_spec=spec,
            computation_fn=computation_fn,
            input_tensor=input_tensor,
            reference_execution=reference_execution,
        )

        meta["classified_intent"] = intent.intent_type
        meta["intent_confidence"] = intent.confidence
        return result, meta
