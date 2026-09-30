"""
hyper_omega/cost_model/ledger.py
Work Ledger and End-to-End Computational Cost Model.
Strictly separates:
- Theoretical operation reduction
- Measured wall-clock latency
- Memory traffic (bytes moved, reads/writes)
- Total End-to-End Cost: T_total = T_analysis_amortized + T_compile_amortized + T_execution + T_verification + T_fallback_expected.
Never derives operation count from latency improvement.
"""
from __future__ import annotations
from enum import Enum
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class MetricProvenance(str, Enum):
    MEASURED = "MEASURED"
    CALCULATED = "CALCULATED"
    THEORETICAL = "THEORETICAL"
    ASSUMED = "ASSUMED"
    SIMULATED = "SIMULATED"
    UNVERIFIED = "UNVERIFIED"


class WorkLedger(BaseModel):
    """Immutable accounting ledger for physical and mathematical operations."""
    workload_id: str
    original_operations: int = 0
    candidate_operations: int = 0
    executed_operations: int = 0
    eliminated_operations: int = 0
    verification_operations: int = 0
    fallback_operations: int = 0
    
    memory_reads_bytes: int = 0
    memory_writes_bytes: int = 0
    total_bytes_moved: int = 0
    
    measured_latency_ms: float = 0.0
    measured_speedup_ratio: float = 1.0
    provenance: MetricProvenance = MetricProvenance.MEASURED

    def compute_elimination_percentage(self) -> float:
        if self.original_operations <= 0:
            return 0.0
        return max(0.0, min(100.0, (self.eliminated_operations / self.original_operations) * 100.0))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "workload_id": self.workload_id,
            "original_operations": self.original_operations,
            "candidate_operations": self.candidate_operations,
            "executed_operations": self.executed_operations,
            "eliminated_operations": self.eliminated_operations,
            "verification_operations": self.verification_operations,
            "elimination_pct": round(self.compute_elimination_percentage(), 2),
            "total_bytes_moved": self.total_bytes_moved,
            "measured_latency_ms": round(self.measured_latency_ms, 3),
            "measured_speedup_ratio": round(self.measured_speedup_ratio, 2),
            "provenance": self.provenance.value,
        }


class EndToEndCostCalculator:
    """Calculates true end-to-end execution cost including analysis and verification overhead."""

    @staticmethod
    def calculate_total_cost_ms(
        t_analysis_ms: float,
        t_compile_ms: float,
        t_exec_ms: float,
        t_verify_ms: float,
        t_fallback_ms: float,
        p_fallback: float = 0.0,
        amortization_factor: int = 1000,
    ) -> Dict[str, float]:
        t_analysis_amortized = t_analysis_ms / max(1, amortization_factor)
        t_compile_amortized = t_compile_ms / max(1, amortization_factor)
        t_total = t_analysis_amortized + t_compile_amortized + t_exec_ms + t_verify_ms + (p_fallback * t_fallback_ms)
        
        return {
            "t_analysis_amortized_ms": round(t_analysis_amortized, 4),
            "t_compile_amortized_ms": round(t_compile_amortized, 4),
            "t_execution_ms": round(t_exec_ms, 4),
            "t_verification_ms": round(t_verify_ms, 4),
            "t_fallback_expected_ms": round(p_fallback * t_fallback_ms, 4),
            "t_total_end_to_end_ms": round(t_total, 4),
        }
