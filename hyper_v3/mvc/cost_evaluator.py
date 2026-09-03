"""
hyper_v3/mvc/cost_evaluator.py
Computes the Minimum Verified Computation total work function:
W_total = arithmetic_work + memory_work + transfer_work + synchronization_work
        + launch_work + allocation_work + conversion_work
"""

from typing import Dict, Any


class TotalWorkRecord:
    """Detailed breakdown of all work components constituting total computational cost."""
    def __init__(
        self,
        arithmetic_flops: int,
        memory_bytes: int,
        transfer_bytes: int = 0,
        sync_overhead_us: float = 0.0,
        launch_overhead_us: float = 0.0,
        allocation_bytes: int = 0,
        conversion_flops: int = 0,
        w_arith_weight: float = 1.0,
        w_mem_weight: float = 4.0,       # 1 byte of memory traffic ~ 4 FLOPs in energy/time
        w_trans_weight: float = 8.0,     # PCI/USM transfers are expensive
        w_sync_weight: float = 100.0,
        w_launch_weight: float = 50.0,
        w_alloc_weight: float = 2.0,
        w_conv_weight: float = 1.5
    ):
        self.arithmetic_flops = arithmetic_flops
        self.memory_bytes = memory_bytes
        self.transfer_bytes = transfer_bytes
        self.sync_overhead_us = sync_overhead_us
        self.launch_overhead_us = launch_overhead_us
        self.allocation_bytes = allocation_bytes
        self.conversion_flops = conversion_flops

        # Weighted composite W_total
        self.w_total = float(
            (arithmetic_flops * w_arith_weight) +
            (memory_bytes * w_mem_weight) +
            (transfer_bytes * w_trans_weight) +
            (sync_overhead_us * w_sync_weight) +
            (launch_overhead_us * w_launch_weight) +
            (allocation_bytes * w_alloc_weight) +
            (conversion_flops * w_conv_weight)
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "w_total": round(self.w_total, 2),
            "arithmetic_flops": self.arithmetic_flops,
            "memory_bytes": self.memory_bytes,
            "transfer_bytes": self.transfer_bytes,
            "sync_overhead_us": round(self.sync_overhead_us, 2),
            "launch_overhead_us": round(self.launch_overhead_us, 2),
            "allocation_bytes": self.allocation_bytes,
            "conversion_flops": self.conversion_flops
        }


class MVCCostEvaluator:
    """Evaluates whether an optimized strategy minimizes W_total compared to baseline."""

    @staticmethod
    def evaluate(
        baseline_record: TotalWorkRecord,
        candidate_record: TotalWorkRecord
    ) -> Dict[str, Any]:
        """Compares baseline vs candidate work across all seven terms."""
        work_avoided = max(0.0, baseline_record.w_total - candidate_record.w_total)
        vwa_ratio = work_avoided / max(baseline_record.w_total, 1.0)
        is_beneficial = candidate_record.w_total < baseline_record.w_total

        return {
            "baseline_w_total": baseline_record.w_total,
            "candidate_w_total": candidate_record.w_total,
            "work_avoided": round(work_avoided, 2),
            "verified_work_avoidance_ratio": round(vwa_ratio, 4),
            "is_beneficial": is_beneficial,
            "breakdown_baseline": baseline_record.to_dict(),
            "breakdown_candidate": candidate_record.to_dict()
        }
