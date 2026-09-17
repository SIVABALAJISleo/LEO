"""
backend/caoe/caoe_engine.py
===========================
CAOE Layer 7: Contract-Aware Optimization Engine Orchestrator.

Coordinates all 6 layers:
1. Contract Analyzer (detect requirements & tolerance sweep)
2. Precision Reducer (FP32 -> FP16 -> INT8 negotiation)
3. Sparsity Detector (structural, temporal, low-rank work elimination)
4. Cache Manager (smart memoization with TTL)
5. CPU+iGPU Scheduler (workload classification & hardware dispatch)
6. Verifier (error boundary & contract satisfaction proof)
7. Telemetry (live metric logging & parity tracking)
"""

from __future__ import annotations

import time
from typing import Any, Callable, Dict, List, Optional, Tuple

import numpy as np

from .contract_analyzer import Contract, ContractAnalyzer, WorkloadSpec
from .precision_reducer import PrecisionReducer
from .sparsity_detector import SparsityDetector
from .cache_manager import CacheManager
from .cpu_igpu_scheduler import CPUiGPUScheduler
from .verifier import Verifier, VerificationResult
from .telemetry import TelemetryLayer


class ContractAwareOptimizationEngine:
    """Master orchestrator for Contract-Aware Optimization."""

    def __init__(self, cache_size_mb: float = 512.0) -> None:
        self.analyzer = ContractAnalyzer()
        self.precision_reducer = PrecisionReducer()
        self.sparsity_detector = SparsityDetector()
        self.cache_manager = CacheManager(max_size_mb=cache_size_mb)
        self.scheduler = CPUiGPUScheduler()
        self.verifier = Verifier()
        self.telemetry = TelemetryLayer()

    def optimize_and_execute(
        self,
        workload_spec: WorkloadSpec,
        computation_fn: Callable[[np.ndarray, int, float], np.ndarray],
        input_tensor: np.ndarray,
        reference_execution: Optional[np.ndarray] = None,
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Execute computation pipeline with full contract optimization.
        Returns (result, execution_metadata).
        """
        t_total_start = time.perf_counter_ns()

        # Step 1: Detect Contract
        contract = self.analyzer.analyze_workload(workload_spec)

        # Baseline execution time measurement for reference
        if reference_execution is None:
            t_ref0 = time.perf_counter_ns()
            reference_execution = computation_fn(input_tensor, 32, 0.0)
            baseline_ms = max(1e-6, (time.perf_counter_ns() - t_ref0) / 1e6)
        else:
            baseline_ms = 1.0

        # Step 2: Caching Check
        cache_hit = False
        if contract.cache_ttl > 0:
            cached_res, cache_meta = self.cache_manager.get_or_compute(
                input_data=input_tensor,
                computation_fn=lambda: reference_execution,
                contract=contract,
            )
            if cache_meta["hit"]:
                exec_ms = cache_meta["latency_ms"]
                speedup = baseline_ms / max(1e-6, exec_ms)
                verif = self.verifier.verify(cached_res, reference_execution, contract)

                self.telemetry.record_execution(
                    execution_id=workload_spec.name,
                    shape=input_tensor.shape,
                    precision=contract.precision,
                    sparsity_eliminated=1.0,
                    executor="cache",
                    latency_ms=exec_ms,
                    speedup=speedup,
                    contract_met=verif.contract_met,
                    error_rel=verif.relative_error,
                    cache_hit=True,
                )

                return cached_res, {
                    "source": "cache",
                    "speedup": speedup,
                    "verification": verif.as_dict(),
                    "contract": contract.__dict__,
                }

        # Step 3a: Sparsity & Redundancy Detection
        sparsity_info = self.sparsity_detector.detect_sparsity(input_tensor, workload_spec)
        sparsity_ratio = sparsity_info["work_elimination"]

        # Step 3b: Precision Reduction Negotiation
        prec_eval_fn = lambda x, p: computation_fn(x, p, sparsity_ratio)
        prec_result = self.precision_reducer.reduce_iteratively(
            computation_fn=prec_eval_fn,
            sample_inputs=[input_tensor],
            contract=contract,
        )
        selected_precision = prec_result["precision"]
        contract.precision = selected_precision

        # Step 3c: Workload Scheduling
        schedule = self.scheduler.schedule(input_tensor.shape, contract, workload_spec.task_type)
        executor = schedule["executor"]

        # Step 4: Optimized Execution
        t0 = time.perf_counter_ns()
        result = computation_fn(input_tensor, selected_precision, sparsity_ratio)
        exec_ms = max(1e-6, (time.perf_counter_ns() - t0) / 1e6)

        # Step 5: Verification & Parity Audit
        verification = self.verifier.verify(result, reference_execution, contract)

        # Fallback if contract is violated
        fallback_used = False
        if not verification.contract_met:
            result = reference_execution
            fallback_used = True
            verification = self.verifier.verify(result, reference_execution, contract)

        speedup = baseline_ms / max(1e-6, exec_ms)

        # Store in cache if enabled
        if contract.cache_ttl > 0:
            self.cache_manager.get_or_compute(
                input_data=input_tensor,
                computation_fn=lambda: result,
                contract=contract,
            )

        # Log telemetry
        self.telemetry.record_execution(
            execution_id=workload_spec.name,
            shape=input_tensor.shape,
            precision=selected_precision,
            sparsity_eliminated=sparsity_ratio,
            executor=executor if not fallback_used else "cpu_fallback",
            latency_ms=exec_ms,
            speedup=speedup if not fallback_used else 1.0,
            contract_met=verification.contract_met,
            error_rel=verification.relative_error,
            cache_hit=False,
            notes=f"strategy={sparsity_info['best_strategy']}",
        )

        metadata = {
            "source": "optimized_caoe" if not fallback_used else "fallback",
            "precision": selected_precision,
            "sparsity_strategy": sparsity_info["best_strategy"],
            "work_elimination_pct": round(sparsity_ratio * 100.0, 1),
            "executor": executor if not fallback_used else "cpu_fallback",
            "latency_ms": round(exec_ms, 4),
            "speedup": round(speedup, 2) if not fallback_used else 1.0,
            "fallback_used": fallback_used,
            "verification": verification.as_dict(),
        }

        return result, metadata
