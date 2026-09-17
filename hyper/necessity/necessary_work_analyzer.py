"""
hyper/necessity/necessary_work_analyzer.py
==========================================
LEO/HYPER Ω — Necessary-Work Minimization Analyzer.

Formal work accounting:
    W_reference:           Total theoretical FLOPs in standard reference algorithm
    W_necessary_estimate:  Minimum theoretical operations required under contract
    W_executed:            Actual operations computed by HYPER
    W_reused:              Operations avoided through cache or structural reuse
    W_eliminated:          W_reference - W_executed

Scientific Principle:
    Work Elimination is an algorithmic metric, NOT a latency speedup.
    Latency Speedup (T_ref / T_HYPER) must always be reported separately.
"""

from __future__ import annotations

import dataclasses
from typing import Any, Dict


@dataclasses.dataclass
class WorkAnalysisReport:
    workload_name: str
    w_reference_flops: float
    w_necessary_flops: float
    w_executed_flops: float
    w_reused_flops: float
    w_eliminated_flops: float
    work_elimination_ratio: float  # 1 - (W_executed / W_reference)
    t_reference_ms: float
    t_hyper_ms: float
    latency_speedup: float         # T_reference / T_hyper
    notes: str = ""

    def as_dict(self) -> Dict[str, Any]:
        return {
            "workload_name": self.workload_name,
            "w_reference_flops": self.w_reference_flops,
            "w_necessary_flops": self.w_necessary_flops,
            "w_executed_flops": self.w_executed_flops,
            "w_reused_flops": self.w_reused_flops,
            "w_eliminated_flops": self.w_eliminated_flops,
            "work_elimination_pct": round(self.work_elimination_ratio * 100.0, 2),
            "t_reference_ms": round(self.t_reference_ms, 4),
            "t_hyper_ms": round(self.t_hyper_ms, 4),
            "latency_speedup": round(self.latency_speedup, 2),
            "notes": self.notes,
        }


    @property
    def work_eliminated_ratio(self) -> float:
        return self.work_elimination_ratio


class NecessaryWorkAnalyzer:
    """Computes and validates work elimination vs measured latency speedup."""

    @staticmethod
    def analyze_gemm_reference_work(A: Any, B: Any) -> float:
        M = A.shape[0]
        K = A.shape[1] if A.ndim > 1 else 1
        N = B.shape[1] if (hasattr(B, "ndim") and B.ndim > 1) else (B.shape[0] if hasattr(B, "shape") else 1)
        return float(2 * M * K * N)

    @staticmethod
    def evaluate_work_reduction(
        w_ref: float,
        w_exec: float,
        t_ref_ms: float,
        t_hyper_ms: float,
        workload_name: str = "tensor_op",
    ) -> WorkAnalysisReport:
        return NecessaryWorkAnalyzer.analyze(
            workload_name=workload_name,
            w_reference=w_ref,
            w_executed=w_exec,
            t_reference_ms=t_ref_ms,
            t_hyper_ms=t_hyper_ms,
        )

    @staticmethod
    def analyze(
        workload_name: str,
        w_reference: float,
        w_executed: float,
        t_reference_ms: float,
        t_hyper_ms: float,
        w_necessary: float = 0.0,
        w_reused: float = 0.0,
        notes: str = "",
    ) -> WorkAnalysisReport:
        w_eliminated = max(0.0, w_reference - w_executed)
        work_elim_ratio = (w_eliminated / w_reference) if w_reference > 0 else 0.0
        speedup = (t_reference_ms / max(1e-9, t_hyper_ms)) if t_reference_ms > 0 else 1.0

        return WorkAnalysisReport(
            workload_name=workload_name,
            w_reference_flops=w_reference,
            w_necessary_flops=w_necessary if w_necessary > 0 else w_executed,
            w_executed_flops=w_executed,
            w_reused_flops=w_reused,
            w_eliminated_flops=w_eliminated,
            work_elimination_ratio=work_elim_ratio,
            t_reference_ms=t_reference_ms,
            t_hyper_ms=t_hyper_ms,
            latency_speedup=speedup,
            notes=notes,
        )

