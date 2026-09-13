#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
universal_compute_router/adaptive_dispatch.py
=============================================
Phase B1: Heterogeneous Dispatch Router for Intel Core i5-12450H & Intel UHD Graphics (48 EUs).

Architectural Principles:
  1. Sub-100µs Dispatch Overhead: All routing decisions use O(1) mathematical lookup rules.
  2. Softmax Pinning: Softmax always executes on CPU P-cores (PCIe/driver overhead > kernel runtime).
  3. Long Attention Offload: Attention operations with seq_len > 2048 route to iGPU (48 EUs).
  4. Dense GEMM Scaling: Tensors >= 262,144 elements (512x512) utilize parallel execution units.
  5. Thermal Envelope Preservation: Sieve/filtering/monitoring tasks route to low-power E-cores.
"""

import time
import logging
from typing import Dict, Any, Tuple, Optional, Callable, List
import math

logger = logging.getLogger("HyperRouter.AdaptiveDispatch")


class AdaptiveDispatchRouter:
    """
    Sub-100µs decision engine for heterogeneous compute dispatch across
    Intel Alder Lake / Golden Cove P-cores, Gracemont E-cores, and Intel UHD Graphics (48 EUs).
    """

    def __init__(self, has_igpu: bool = True, hardware_target: str = "i5-12450H"):
        self.has_igpu = has_igpu
        self.hardware_target = hardware_target
        self.decision_latencies_us: List[float] = []
        self.route_counts: Dict[str, int] = {
            "CPU_PCORE": 0,
            "CPU_ECORE": 0,
            "IGPU_48EU": 0,
        }
        # Pre-warm JIT / cache
        self.route("warmup", (1,))
        self.decision_latencies_us.clear()
        self.route_counts = {"CPU_PCORE": 0, "CPU_ECORE": 0, "IGPU_48EU": 0}

    def route(
        self,
        op_name: str,
        tensor_shape: Tuple[int, ...],
        seq_len: int = 1,
        sparsity_ratio: float = 0.0,
    ) -> Dict[str, Any]:
        """
        Calculates optimal execution target in sub-100 microseconds.
        """
        t0 = time.perf_counter_ns()
        op_lower = op_name.lower()
        num_elements = math.prod(tensor_shape) if tensor_shape else 0

        # Rule 1: Softmax always pinned to CPU P-Core
        # (Driver invocation overhead ~150-300µs, kernel runtime ~10-40µs)
        if "softmax" in op_lower:
            target = "CPU_PCORE"
            reason = "Softmax dispatch latency penalty exceeds kernel execution time."

        # Rule 2: Long sequence attention (> 2048 tokens) routes to iGPU
        elif "attention" in op_lower and seq_len > 2048 and self.has_igpu:
            target = "IGPU_48EU"
            reason = f"Long sequence attention (seq_len={seq_len}) amortizes iGPU setup cost."

        # Rule 3: High-density GEMM / Linear projection (>= 262,144 elements)
        elif ("gemm" in op_lower or "linear" in op_lower or "matmul" in op_lower) and num_elements >= 262144:
            if self.has_igpu:
                target = "IGPU_48EU"
                reason = f"High FLOP/byte arithmetic intensity ({num_elements} elements) saturates 48 EUs."
            else:
                target = "CPU_PCORE"
                reason = f"Large GEMM ({num_elements} elements) routed to AVX2 P-core SIMD units."

        # Rule 4: Memory-bandwidth bound vector reduction / normalization
        elif "norm" in op_lower or "reduce" in op_lower or "add" in op_lower:
            target = "CPU_PCORE"
            reason = "Memory-bandwidth bound vector reduction executes with minimal cache misses on P-core."

        # Rule 5: Low-power background monitoring, sieve, delta tracking
        elif "sieve" in op_lower or "delta" in op_lower or "monitor" in op_lower or "filter" in op_lower:
            target = "CPU_ECORE"
            reason = "Low-power Gracemont E-core preserves 45W thermal package budget."

        # Rule 6: Sparse computation fallback
        elif sparsity_ratio > 0.8:
            target = "CPU_PCORE"
            reason = "High sparsity (>80%) favors irregular memory access on CPU cache hierarchy."

        else:
            target = "CPU_PCORE"
            reason = "Standard latency-optimized CPU execution path."

        decision_us = (time.perf_counter_ns() - t0) / 1000.0
        self.decision_latencies_us.append(decision_us)
        self.route_counts[target] = self.route_counts.get(target, 0) + 1

        return {
            "op": op_name,
            "shape": list(tensor_shape),
            "seq_len": seq_len,
            "target": target,
            "decision_latency_us": round(decision_us, 2),
            "reason": reason,
        }

    def dispatch_and_execute(
        self,
        op_name: str,
        tensor_shape: Tuple[int, ...],
        fn: Callable,
        *args,
        seq_len: int = 1,
        **kwargs,
    ) -> Tuple[Any, Dict[str, Any]]:
        """
        Routes the operation and executes the callable, returning (result, routing_metadata).
        """
        route_meta = self.route(op_name, tensor_shape, seq_len=seq_len)
        t_exec_start = time.perf_counter()
        result = fn(*args, **kwargs)
        exec_ms = (time.perf_counter() - t_exec_start) * 1000.0
        route_meta["execution_ms"] = round(exec_ms, 3)
        return result, route_meta

    def get_performance_summary(self) -> Dict[str, Any]:
        """
        Returns average decision overhead and dispatch breakdown.
        """
        if not self.decision_latencies_us:
            return {
                "hardware_target": self.hardware_target,
                "total_dispatches": 0,
                "mean_decision_us": 0.0,
                "p99_decision_us": 0.0,
                "sub_100us_guarantee_met": True,
                "route_distribution": self.route_counts,
            }
        
        sorted_times = sorted(self.decision_latencies_us)
        n = len(sorted_times)
        avg_overhead = sum(sorted_times) / n
        p99_idx = min(n - 1, int(0.99 * n))
        p99_overhead = sorted_times[p99_idx]

        return {
            "hardware_target": self.hardware_target,
            "total_dispatches": n,
            "mean_decision_us": round(avg_overhead, 2),
            "p99_decision_us": round(p99_overhead, 2),
            "sub_100us_guarantee_met": p99_overhead < 100.0,
            "route_distribution": self.route_counts,
        }
