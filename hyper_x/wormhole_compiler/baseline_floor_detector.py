import json
import time
from dataclasses import dataclass, asdict, field
from typing import Dict, Any, List, Optional
import numpy as np

@dataclass
class BaselineFloorReport:
    workload: str
    baseline: str
    baseline_time: float
    known_alternatives: List[str]
    best_known_local_route: str
    optimization_slack: float
    status: str
    scope: Dict[str, str]
    theoretical_roofline_time: Optional[float] = None
    roofline_efficiency: Optional[float] = None
    arithmetic_intensity: Optional[float] = None
    peak_gflops: Optional[float] = None
    peak_bandwidth_gbps: Optional[float] = None
    reason: Optional[str] = None
    evidence: Dict[str, Any] = field(default_factory=dict)

class BaselineFloorDetector:
    def __init__(self, default_peak_gflops: float = 120.0, default_peak_bandwidth_gbps: float = 40.0):
        self.default_peak_gflops = default_peak_gflops
        self.default_peak_bandwidth_gbps = default_peak_bandwidth_gbps

    def analyze(
        self,
        workload_name: str,
        baseline_impl: str,
        baseline_time: float,
        hardware_scope: str,
        contract_id: str,
        workload: Any = None,
        flops: float = 0.0,
        bytes_transferred: float = 0.0,
        peak_gflops: Optional[float] = None,
        peak_bandwidth_gbps: Optional[float] = None,
    ) -> BaselineFloorReport:
        gflops = peak_gflops or self.default_peak_gflops
        bw_gbps = peak_bandwidth_gbps or self.default_peak_bandwidth_gbps
        
        calc_flops = flops
        calc_bytes = bytes_transferred
        if workload is not None and isinstance(workload, np.ndarray):
            itemsize = workload.itemsize
            if workload.ndim == 2:
                M, K = workload.shape
                if calc_flops <= 0.0:
                    calc_flops = 2.0 * M * K * K
                if calc_bytes <= 0.0:
                    calc_bytes = (2.0 * M * K + K * K) * itemsize
            elif workload.ndim == 1:
                N = workload.size
                if calc_flops <= 0.0:
                    calc_flops = float(N)
                if calc_bytes <= 0.0:
                    calc_bytes = float(N * itemsize)

        t_compute = (calc_flops / (gflops * 1e9)) if calc_flops > 0 else 0.0
        t_memory = (calc_bytes / (bw_gbps * 1e9)) if calc_bytes > 0 else 0.0
        t_roofline = max(t_compute, t_memory)
        
        arithmetic_intensity = (calc_flops / calc_bytes) if calc_bytes > 0 else 0.0
        
        if baseline_time > 0 and t_roofline > 0:
            efficiency = min(1.0, t_roofline / baseline_time)
        else:
            efficiency = 1.0 if baseline_time < 1e-4 else 0.1

        slack = max(0.0, baseline_time - t_roofline) if t_roofline > 0 else max(0.0, baseline_time - 1e-4)
        
        if efficiency >= 0.65 or baseline_time < 1e-4:
            status = "BASELINE_NEAR_PRACTICAL_FLOOR"
            reason = f"Baseline achieves {efficiency*100:.1f}% of theoretical hardware roofline limit; remaining optimization slack is negligible ({slack*1000.0:.3f} ms)"
        elif efficiency >= 0.30:
            status = "BASELINE_HAS_MODERATE_SLACK"
            reason = f"Baseline achieves {efficiency*100:.1f}% of roofline limit; moderate algorithmic/kernel tuning headroom exists"
        else:
            status = "BASELINE_HAS_SIGNIFICANT_SLACK"
            reason = f"Baseline achieves only {efficiency*100:.1f}% of roofline limit; significant headroom exists for memory or compute restructuring"
            
        report = BaselineFloorReport(
            workload=workload_name,
            baseline=baseline_impl,
            baseline_time=baseline_time,
            known_alternatives=["numpy", "scipy.sparse", "numba", "openblas"],
            best_known_local_route=baseline_impl,
            optimization_slack=slack,
            status=status,
            scope={
                "hardware": hardware_scope,
                "software": "python/native",
                "contract": contract_id,
                "algorithm_family": "dense_linear_algebra" if (workload is not None and isinstance(workload, np.ndarray)) else "unknown"
            },
            theoretical_roofline_time=t_roofline if t_roofline > 0 else None,
            roofline_efficiency=round(efficiency, 4),
            arithmetic_intensity=round(arithmetic_intensity, 4) if arithmetic_intensity > 0 else None,
            peak_gflops=gflops,
            peak_bandwidth_gbps=bw_gbps,
            reason=reason,
            evidence={
                "t_compute_sec": t_compute,
                "t_memory_sec": t_memory,
                "calc_flops": calc_flops,
                "calc_bytes": calc_bytes,
                "efficiency": efficiency
            }
        )
        return report

    def save_report(self, report: BaselineFloorReport, filepath: str = "BASELINE_FLOOR_REPORT.json"):
        with open(filepath, "w") as f:
            json.dump(asdict(report), f, indent=2)

