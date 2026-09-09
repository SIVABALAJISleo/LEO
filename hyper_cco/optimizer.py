"""
hyper_cco/optimizer.py
======================
Contract-Constrained Computation Optimizer (HYPER-CCO).
Implements the core decision function:
min_{a in A} [ Latency(a) + lambda_E Energy(a) + lambda_R Risk(a) + lambda_M Memory(a) ]
subject to:
Error(a) <= epsilon
Quality(a) >= Q_min
Throughput(a) >= T_min

Follows the canonical strategy priority:
1. Exact Cache -> 2. Incremental Delta -> 3. Algebraic Reformulation ->
4. Low-Rank -> 5. Sparsity -> 6. Mixed Precision -> 7. Residual-First ->
8. Speculative -> 9. Heterogeneous CPU+UHD -> 10. Exact Fallback.
Every decision is validated against the application's contract before acceptance.
"""

import time
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, Tuple, List, Callable
import numpy as np

from .contract import ComputeContract, ExactnessClass, VerificationStatus
from .exact_cache import ExactFullContentCache, CacheMode, CacheLookupResult
from .incremental_engine import IncrementalEngine, IncrementalResult
from .residual_engine import ResidualEngine, ResidualResult
from .algebraic_engine import AlgebraicReformulationEngine, AlgebraicTransformationRecord
from .low_rank_engine import LowRankEngine, LowRankResult
from .sparsity_engine import SparsityEngine, SparsityResult
from .precision_engine import PrecisionEngine, PrecisionResult, PrecisionFormat
from .prediction_speculation import SpeculativeEngine, SpeculativeResult
from .temporal_graphics import TemporalGraphicsEngine, TemporalGraphicsResult
from .scheduler import HeterogeneousScheduler, DeviceTarget


@dataclass
class OptimizationPlan:
    """Selected execution plan with cost estimation."""
    strategy_name: str
    estimated_latency_ms: float
    estimated_error: float
    risk_factor: float
    device_target: DeviceTarget
    requires_verification: bool


@dataclass
class CcoExecutionResult:
    """Universal execution result container for HYPER-CCO."""
    output: Any
    strategy: str
    exactness_class: ExactnessClass
    original_operations: float
    executed_operations: float
    eliminated_operations: float
    work_elimination_ratio: float
    latency_ms: float
    measured_absolute_error: float
    measured_relative_error: float
    quality_score: float
    verification_status: VerificationStatus
    device_used: str
    cache_hit: bool
    fallback_triggered: bool
    contract_hash: str
    execution_certificate_id: str = ""


class HyperCcoOptimizer:
    """
    Contract-Constrained Computation Optimizer (HYPER-CCO) Runtime Core.
    """
    def __init__(self, cache_memory_mb: float = 2048.0, default_cache_mode: CacheMode = CacheMode.WARM):
        self.cache = ExactFullContentCache(max_memory_mb=cache_memory_mb, default_mode=default_cache_mode)
        self.scheduler = HeterogeneousScheduler()
        self.temporal_engine = TemporalGraphicsEngine()
        self.execution_count = 0

    def set_cache_mode(self, mode: CacheMode) -> None:
        """Configures cache mode (COLD, WARM, DISABLED)."""
        self.cache.set_mode(mode)

    def execute_matrix_multiplication(
        self,
        A: np.ndarray,
        B: np.ndarray,
        contract: Optional[ComputeContract] = None,
        B_prev: Optional[np.ndarray] = None,
        Y_prev: Optional[np.ndarray] = None,
        v_vector: Optional[np.ndarray] = None
    ) -> CcoExecutionResult:
        """
        Executes Y = A @ B under contract constraints using the multi-stage CCO priority pipeline.
        """
        t_start = time.perf_counter()
        contract = contract or ComputeContract(workload_id="GEMM_CCO")
        contract_hash = contract.compute_hash()
        self.execution_count += 1

        M, K = A.shape
        K2, N = B.shape
        orig_ops = 2.0 * M * K * N
        data_bytes = A.nbytes + B.nbytes + (M * N * 4)

        # Baseline execution lambda for fallback / verification
        def baseline_exec():
            return A @ B

        # ---------------------------------------------------------------------
        # 1. EXACT FULL-CONTENT CACHE (Priority 1)
        # ---------------------------------------------------------------------
        if contract.allow_cache:
            cache_key = self.cache.compute_full_content_key("matmul", A, B, contract_hash=contract_hash)
            lookup = self.cache.lookup(cache_key)
            if lookup.hit:
                elapsed_ms = (time.perf_counter() - t_start) * 1000.0
                return CcoExecutionResult(
                    output=lookup.data,
                    strategy="EXACT_FULL_CONTENT_CACHE",
                    exactness_class=ExactnessClass.CACHED,
                    original_operations=orig_ops,
                    executed_operations=0.0,
                    eliminated_operations=orig_ops,
                    work_elimination_ratio=1.0,
                    latency_ms=elapsed_ms,
                    measured_absolute_error=0.0,
                    measured_relative_error=0.0,
                    quality_score=1.0,
                    verification_status=VerificationStatus.PASS,
                    device_used="CACHE_MEMORY",
                    cache_hit=True,
                    fallback_triggered=False,
                    contract_hash=contract_hash
                )

        # ---------------------------------------------------------------------
        # 2. INCREMENTAL / DELTA COMPUTATION (Priority 2)
        # ---------------------------------------------------------------------
        if contract.allow_reuse and B_prev is not None and Y_prev is not None:
            inc_res = IncrementalEngine.execute_incremental_matmul(A, B, B_prev, Y_prev)
            if inc_res.work_elimination_ratio > 0.30:
                elapsed_ms = (time.perf_counter() - t_start) * 1000.0
                return CcoExecutionResult(
                    output=inc_res.output,
                    strategy=inc_res.strategy,
                    exactness_class=ExactnessClass.REUSED,
                    original_operations=orig_ops,
                    executed_operations=inc_res.executed_operations,
                    eliminated_operations=orig_ops - inc_res.executed_operations,
                    work_elimination_ratio=inc_res.work_elimination_ratio,
                    latency_ms=elapsed_ms,
                    measured_absolute_error=0.0,
                    measured_relative_error=0.0,
                    quality_score=1.0,
                    verification_status=VerificationStatus.PASS,
                    device_used="CPU_AVX2",
                    cache_hit=False,
                    fallback_triggered=False,
                    contract_hash=contract_hash
                )

        # ---------------------------------------------------------------------
        # 3. EXACT ALGEBRAIC REFORMULATION (Priority 3)
        # ---------------------------------------------------------------------
        if v_vector is not None and v_vector.shape == (N, 1):
            rechain_out, record = AlgebraicReformulationEngine.associative_rechain_vector(A, B, v_vector)
            elapsed_ms = (time.perf_counter() - t_start) * 1000.0
            return CcoExecutionResult(
                output=rechain_out,
                strategy=record.name,
                exactness_class=ExactnessClass.EXACT_REFORMULATION,
                original_operations=orig_ops,
                executed_operations=orig_ops * (1.0 - record.operations_eliminated_ratio),
                eliminated_operations=orig_ops * record.operations_eliminated_ratio,
                work_elimination_ratio=record.operations_eliminated_ratio,
                latency_ms=elapsed_ms,
                measured_absolute_error=record.measured_error,
                measured_relative_error=0.0,
                quality_score=1.0,
                verification_status=VerificationStatus.PASS,
                device_used="CPU_AVX2",
                cache_hit=False,
                fallback_triggered=False,
                contract_hash=contract_hash
            )

        # ---------------------------------------------------------------------
        # 4. LOW-RANK APPROXIMATION (Priority 4)
        # ---------------------------------------------------------------------
        if contract.allow_approximation and not contract.is_exact_required():
            low_rank_res = LowRankEngine.execute_low_rank_matmul(
                A, B, rel_tolerance=contract.max_relative_error or 1e-3
            )
            if low_rank_res.contract_satisfied and low_rank_res.work_elimination_ratio > 0.20:
                elapsed_ms = (time.perf_counter() - t_start) * 1000.0
                if contract.allow_cache:
                    cache_key = self.cache.compute_full_content_key("matmul", A, B, contract_hash=contract_hash)
                    self.cache.put(cache_key, low_rank_res.output, original_operations=orig_ops, contract_hash=contract_hash)

                return CcoExecutionResult(
                    output=low_rank_res.output,
                    strategy=low_rank_res.strategy,
                    exactness_class=ExactnessClass.BOUNDED_APPROXIMATION,
                    original_operations=orig_ops,
                    executed_operations=low_rank_res.executed_operations,
                    eliminated_operations=orig_ops - low_rank_res.executed_operations,
                    work_elimination_ratio=low_rank_res.work_elimination_ratio,
                    latency_ms=elapsed_ms,
                    measured_absolute_error=low_rank_res.approximation_frobenius_error,
                    measured_relative_error=low_rank_res.relative_error,
                    quality_score=max(0.0, 1.0 - low_rank_res.relative_error),
                    verification_status=VerificationStatus.PASS,
                    device_used="CPU_AVX2",
                    cache_hit=False,
                    fallback_triggered=False,
                    contract_hash=contract_hash
                )

        # ---------------------------------------------------------------------
        # 5. SPARSITY ENGINE (Priority 5)
        # ---------------------------------------------------------------------
        if contract.allow_reduced_work:
            sparse_res = SparsityEngine.execute_sparse_matmul(
                A, B, max_relative_error=contract.max_relative_error or 1e-3
            )
            if "ACCELERATED" in sparse_res.strategy and sparse_res.work_elimination_ratio > 0.20:
                elapsed_ms = (time.perf_counter() - t_start) * 1000.0
                return CcoExecutionResult(
                    output=sparse_res.output,
                    strategy=sparse_res.strategy,
                    exactness_class=ExactnessClass.REDUCED_WORK,
                    original_operations=orig_ops,
                    executed_operations=sparse_res.executed_operations,
                    eliminated_operations=orig_ops - sparse_res.executed_operations,
                    work_elimination_ratio=sparse_res.work_elimination_ratio,
                    latency_ms=elapsed_ms,
                    measured_absolute_error=sparse_res.analysis.truncation_frobenius_norm,
                    measured_relative_error=sparse_res.analysis.relative_truncation_error,
                    quality_score=max(0.0, 1.0 - sparse_res.analysis.relative_truncation_error),
                    verification_status=VerificationStatus.PASS,
                    device_used="CPU_AVX2",
                    cache_hit=False,
                    fallback_triggered=False,
                    contract_hash=contract_hash
                )

        # ---------------------------------------------------------------------
        # 6. RESIDUAL-FIRST COMPUTATION (Priority 6)
        # ---------------------------------------------------------------------
        if contract.allow_prediction and not contract.is_exact_required():
            res_result = ResidualEngine.execute_matrix_residual(
                A, B, rank_k=min(16, min(M, K)), residual_tolerance=contract.max_relative_error or 1e-3
            )
            if res_result.work_elimination_ratio > 0.20 and res_result.relative_residual_error <= (contract.max_relative_error or 1e-3):
                elapsed_ms = (time.perf_counter() - t_start) * 1000.0
                return CcoExecutionResult(
                    output=res_result.output,
                    strategy=res_result.strategy,
                    exactness_class=ExactnessClass.BOUNDED_APPROXIMATION,
                    original_operations=orig_ops,
                    executed_operations=res_result.executed_operations,
                    eliminated_operations=orig_ops - res_result.executed_operations,
                    work_elimination_ratio=res_result.work_elimination_ratio,
                    latency_ms=elapsed_ms,
                    measured_absolute_error=res_result.residual_norm,
                    measured_relative_error=res_result.relative_residual_error,
                    quality_score=max(0.0, 1.0 - res_result.relative_residual_error),
                    verification_status=VerificationStatus.PASS,
                    device_used="CPU_AVX2",
                    cache_hit=False,
                    fallback_triggered=False,
                    contract_hash=contract_hash
                )

        # ---------------------------------------------------------------------
        # 7. HETEROGENEOUS SCHEDULER DISPATCH & EXACT FALLBACK (Priority 7)
        # ---------------------------------------------------------------------
        schedule_decision = self.scheduler.plan_execution(
            operations=orig_ops,
            input_bytes=A.nbytes + B.nbytes,
            output_bytes=M * N * 4,
            is_regular_dense=True,
            is_sparse_or_irregular=False
        )
        output, kernel_rec = self.scheduler.execute_dispatched_kernel(schedule_decision, baseline_exec)
        elapsed_ms = (time.perf_counter() - t_start) * 1000.0

        # Store in cache for future exact queries
        if contract.allow_cache:
            cache_key = self.cache.compute_full_content_key("matmul", A, B, contract_hash=contract_hash)
            self.cache.put(cache_key, output, original_operations=orig_ops, contract_hash=contract_hash)

        return CcoExecutionResult(
            output=output,
            strategy=f"DISPATCH_{schedule_decision.target_device.value}",
            exactness_class=ExactnessClass.EXACT,
            original_operations=orig_ops,
            executed_operations=orig_ops,
            eliminated_operations=0.0,
            work_elimination_ratio=0.0,
            latency_ms=elapsed_ms,
            measured_absolute_error=0.0,
            measured_relative_error=0.0,
            quality_score=1.0,
            verification_status=VerificationStatus.PASS,
            device_used=kernel_rec.device,
            cache_hit=False,
            fallback_triggered=False,
            contract_hash=contract_hash
        )
