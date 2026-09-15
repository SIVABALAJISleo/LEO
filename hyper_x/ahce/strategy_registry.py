"""
hyper_x/ahce/strategy_registry.py
=================================
Pluggable strategy registry for AHCE (Section 7).
"""

from __future__ import annotations
import abc
import time
from typing import Dict, Any, List, Optional, Tuple
import numpy as np

from .contract import AHCEContract, CorrectnessClass
from .candidate import AHCECandidate, AHCETrialResult
from .workload_signature import WorkloadSignature
from hyper.cache.exact_cache import ExactCache, compute_cache_key
from hyper.low_rank.low_rank_engine import LowRankEngine
from hyper.sparsity.sparsity_engine import SparsityEngine


class AHCEStrategy(abc.ABC):
    """Abstract base class for all pluggable AHCE computational strategies."""

    def __init__(self, name: str, declared_correctness: CorrectnessClass):
        self.name = name
        self.declared_correctness = declared_correctness

    @abc.abstractmethod
    def can_apply(self, signature: WorkloadSignature, contract: AHCEContract) -> bool:
        """Determines whether this strategy can mathematically satisfy the contract."""
        pass

    @abc.abstractmethod
    def estimate(self, signature: WorkloadSignature, hardware: Dict[str, Any]) -> Dict[str, float]:
        """Returns estimated {predicted_work_units, predicted_latency_ms, transformation_cost_ms}."""
        pass

    @abc.abstractmethod
    def execute(self, A: np.ndarray, B: Optional[np.ndarray], contract: AHCEContract) -> Tuple[Any, Dict[str, Any]]:
        """Executes the strategy on host hardware. Returns (output, telemetry)."""
        pass

    @abc.abstractmethod
    def explain(self) -> str:
        """Human-readable scientific rationale."""
        pass

    @abc.abstractmethod
    def failure_modes(self) -> List[str]:
        """Known boundary conditions where this strategy fails."""
        pass


class DenseBaselineStrategy(AHCEStrategy):
    """Reference dense execution on CPU AVX2 (irreducible fallback)."""

    def __init__(self):
        super().__init__("dense_baseline", CorrectnessClass.EXACT)

    def can_apply(self, signature: WorkloadSignature, contract: AHCEContract) -> bool:
        return True  # Universal fallback

    def estimate(self, signature: WorkloadSignature, hardware: Dict[str, Any]) -> Dict[str, float]:
        dims = signature.features.dimensions
        M = dims[0] if len(dims) > 0 else 1
        K = dims[1] if len(dims) > 1 else 1
        ops = float(2 * M * K * K)
        return {
            "predicted_work_units": ops,
            "predicted_latency_ms": max(0.1, ops / (400e6)),  # ~400 GFLOP/s on AVX2
            "transformation_cost_ms": 0.0
        }

    def execute(self, A: np.ndarray, B: Optional[np.ndarray], contract: AHCEContract) -> Tuple[Any, Dict[str, Any]]:
        t0 = time.perf_counter_ns()
        if B is not None:
            C = A @ B
        else:
            C = A.copy()
        lat = (time.perf_counter_ns() - t0) / 1e6
        return C, {"execution_ms": lat, "strategy": self.name, "path_class": "EXACT"}

    def explain(self) -> str:
        return "Standard dense matrix multiplication using host vector SIMD FMA (zero elimination)."

    def failure_modes(self) -> List[str]:
        return ["Out of memory on massive dimensions ($N > 16384$)"]


class ExactCacheStrategy(AHCEStrategy):
    """Cryptographic multi-state cache strategy."""

    def __init__(self):
        super().__init__("exact_cache", CorrectnessClass.CACHED)
        self.cache = ExactCache()

    def can_apply(self, signature: WorkloadSignature, contract: AHCEContract) -> bool:
        return contract.allow_cache

    def estimate(self, signature: WorkloadSignature, hardware: Dict[str, Any]) -> Dict[str, float]:
        return {
            "predicted_work_units": 0.0,
            "predicted_latency_ms": 0.002,
            "transformation_cost_ms": 0.001
        }

    def execute(self, A: np.ndarray, B: Optional[np.ndarray], contract: AHCEContract) -> Tuple[Any, Dict[str, Any]]:
        t0 = time.perf_counter_ns()
        key = compute_cache_key(A, model_identifier="ahce_tensor")
        val, is_hit, _ = self.cache.get(key)
        lat = (time.perf_counter_ns() - t0) / 1e6

        if is_hit:
            return val, {"execution_ms": lat, "cache_hit": True, "strategy": self.name}

        # Cache miss: compute reference and populate
        C = A @ B if B is not None else A
        self.cache.put(key, C)
        return C, {"execution_ms": lat, "cache_hit": False, "strategy": self.name}

    def explain(self) -> str:
        return "Retrieves previously computed bit-exact output via 256-bit cryptographic state hash."

    def failure_modes(self) -> List[str]:
        return ["Novel inputs (cache miss)", "Altered floating point seed / compiler flags"]


class LowRankSVDStrategy(AHCEStrategy):
    """Randomized SVD factorization strategy."""

    def __init__(self, default_rank: int = 16):
        super().__init__("low_rank_svd", CorrectnessClass.BOUNDED_APPROXIMATION)
        self.engine = LowRankEngine(default_rank=default_rank)

    def can_apply(self, signature: WorkloadSignature, contract: AHCEContract) -> bool:
        if not contract.allow_approximation and contract.correctness_class not in (
            CorrectnessClass.NUMERICALLY_EQUIVALENT,
            CorrectnessClass.BOUNDED_APPROXIMATION,
            CorrectnessClass.CONTRACT_EQUIVALENT
        ):
            return False
        dims = signature.features.dimensions
        return len(dims) == 2 and min(dims) >= 32 and (signature.features.estimated_effective_rank or 999) < min(dims)

    def estimate(self, signature: WorkloadSignature, hardware: Dict[str, Any]) -> Dict[str, float]:
        dims = signature.features.dimensions
        M, K = dims[0], dims[1]
        r = signature.features.estimated_effective_rank or 16
        factored_ops = float(2 * M * r * K)
        return {
            "predicted_work_units": factored_ops,
            "predicted_latency_ms": max(0.05, factored_ops / (400e6)),
            "transformation_cost_ms": max(0.05, (2 * M * r * K) / (400e6))
        }

    def execute(self, A: np.ndarray, B: Optional[np.ndarray], contract: AHCEContract) -> Tuple[Any, Dict[str, Any]]:
        t0 = time.perf_counter_ns()
        if B is None:
            B = np.eye(A.shape[1], dtype=A.dtype)
        tol = contract.max_relative_error or 1e-3
        out, telem = self.engine.benchmark_and_execute(A, B, max_allowed_rel_error=tol)
        lat = (time.perf_counter_ns() - t0) / 1e6
        telem["total_strategy_latency_ms"] = lat
        telem["strategy"] = self.name
        return out, telem

    def explain(self) -> str:
        return "Approximates A via rank-r randomized SVD factorization, evaluating associative contraction in O(r N^2)."

    def failure_modes(self) -> List[str]:
        return ["Full-rank white noise matrices", "Strict bit-exact contracts (max_abs_error=0)"]


class SparseCSRStrategy(AHCEStrategy):
    """Overhead-gated Compressed Sparse Row strategy."""

    def __init__(self, default_threshold: float = 1e-5):
        super().__init__("sparse_csr", CorrectnessClass.REDUCED_WORK)
        self.engine = SparsityEngine(default_threshold=default_threshold)

    def can_apply(self, signature: WorkloadSignature, contract: AHCEContract) -> bool:
        return signature.features.sparsity >= 0.60

    def estimate(self, signature: WorkloadSignature, hardware: Dict[str, Any]) -> Dict[str, float]:
        dims = signature.features.dimensions
        M, K = dims[0], dims[1]
        dense_ops = float(2 * M * K * K)
        sparse_ops = dense_ops * (1.0 - signature.features.sparsity)
        return {
            "predicted_work_units": sparse_ops,
            "predicted_latency_ms": max(0.05, sparse_ops / (250e6)),
            "transformation_cost_ms": 0.05
        }

    def execute(self, A: np.ndarray, B: Optional[np.ndarray], contract: AHCEContract) -> Tuple[Any, Dict[str, Any]]:
        t0 = time.perf_counter_ns()
        if B is None:
            B = np.eye(A.shape[1], dtype=A.dtype)
        tol = contract.max_relative_error or 1e-4
        out, telem = self.engine.execute_with_overhead_check(A, B, max_allowed_error=tol)
        lat = (time.perf_counter_ns() - t0) / 1e6
        telem["total_strategy_latency_ms"] = lat
        telem["strategy"] = self.name
        return out, telem

    def explain(self) -> str:
        return "Converts sparse matrix to CSR format and executes sparse-dense contraction, skipping all structural zeros."

    def failure_modes(self) -> List[str]:
        return ["Dense matrices (density > 0.40) where pointer-chasing overhead exceeds dense FMA speed"]


class AHCEStrategyRegistry:
    """Registry managing all active computational strategies."""

    def __init__(self):
        self._strategies: Dict[str, AHCEStrategy] = {}
        self.register(DenseBaselineStrategy())
        self.register(ExactCacheStrategy())
        self.register(LowRankSVDStrategy())
        self.register(SparseCSRStrategy())

    def register(self, strategy: AHCEStrategy) -> None:
        self._strategies[strategy.name] = strategy

    def get(self, name: str) -> Optional[AHCEStrategy]:
        return self._strategies.get(name)

    def list_strategies(self) -> List[str]:
        return list(self._strategies.keys())

    def get_applicable(self, signature: WorkloadSignature, contract: AHCEContract) -> List[AHCEStrategy]:
        return [s for s in self._strategies.values() if s.can_apply(signature, contract)]
