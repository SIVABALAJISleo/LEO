"""
hyper/cpu/affinity_governor.py
==============================
CPU Affinity & Thread Governor for Intel Core i5-12450H (4 P-cores + 4 E-cores).
Pins latency-critical tasks to Golden Cove P-cores.
"""

import os
import psutil
from typing import Dict, Any, List


class CpuAffinityGovernor:
    """
    Manages process and thread affinity across Intel Alder Lake P-cores and E-cores.
    """
    def __init__(self):
        self.p_core_logical_ids = [0, 1, 2, 3, 4, 5, 6, 7] # 4 P-cores (8 threads via HyperThreading)
        self.e_core_logical_ids = [8, 9, 10, 11] # 4 E-cores (single-threaded)

    def pin_to_p_cores(self) -> Dict[str, Any]:
        try:
            p = psutil.Process(os.getpid())
            p.cpu_affinity(self.p_core_logical_ids)
            return {"status": "SUCCESS", "affinity_mask": self.p_core_logical_ids, "pinned_to": "P_CORES"}
        except Exception as e:
            return {"status": "FALLBACK", "error": str(e), "affinity_mask": "ALL"}

    def reset_affinity(self) -> Dict[str, Any]:
        try:
            p = psutil.Process(os.getpid())
            all_cores = list(range(psutil.cpu_count(logical=True) or 12))
            p.cpu_affinity(all_cores)
            return {"status": "SUCCESS", "affinity_mask": all_cores}
        except Exception as e:
            return {"status": "FALLBACK", "error": str(e)}
