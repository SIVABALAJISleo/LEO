"""
hyper/microtask/microtask_scheduler.py
======================================
Micro-Task Scheduler (Section 31):
Splits large workloads into adaptive regions. Dynamically assigns:
- CPU P-cores (irregular, latency-critical)
- CPU E-cores (background compaction, telemetry)
- Intel UHD iGPU (large regular tiles)
"""

from typing import Dict, Any, List, Tuple
from dataclasses import dataclass, field


@dataclass
class MicroTask:
    task_id: str
    region_offset: Tuple[int, ...]
    region_size: Tuple[int, ...]
    assigned_device: str  # "CPU_P_CORE", "CPU_E_CORE", "INTEL_UHD"
    priority: int = 1


class MicroTaskScheduler:
    """
    Decomposes tensors into micro-tasks and balances device dispatching.
    """
    def __init__(self, tile_size: int = 128):
        self.tile_size = tile_size

    def partition_tensor_2d(self, rows: int, cols: int) -> List[MicroTask]:
        tasks = []
        task_idx = 0
        ts = self.tile_size

        for r in range(0, rows, ts):
            r_len = min(ts, rows - r)
            for c in range(0, cols, ts):
                c_len = min(ts, cols - c)
                
                # Dynamic device allocation: Edge/irregular tiles -> CPU P-core; bulk tiles -> Intel UHD
                device = "INTEL_UHD" if (r_len == ts and c_len == ts and rows >= 512) else "CPU_P_CORE"
                tasks.append(MicroTask(
                    task_id=f"mt_{task_idx}",
                    region_offset=(r, c),
                    region_size=(r_len, c_len),
                    assigned_device=device
                ))
                task_idx += 1
        return tasks
