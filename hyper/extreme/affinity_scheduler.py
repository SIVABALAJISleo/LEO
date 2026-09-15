"""
hyper/extreme/affinity_scheduler.py
===================================
Alder Lake Core Affinity Pinning Scheduler for Intel Core i5-12450H on Windows 11.

Hardware Architecture:
- 4 Performance-cores (P-cores) with Hyper-Threading: 8 logical threads (0 - 7).
- 4 Efficient-cores (E-cores) without Hyper-Threading: 4 logical threads (8 - 11).
- Total: 12 logical processors.

Strategy:
- Pin critical synchronous compute loops exclusively to P-cores (0 - 7).
- Delegate asynchronous telemetry, L3 cache eviction checks, and background logging
  exclusively to E-cores (8 - 11) to eliminate Thread Director migration jitter.
"""

from contextlib import contextmanager
import ctypes
from dataclasses import dataclass
import os
import psutil
import threading
from typing import Callable, Generator, List, Optional


@dataclass(frozen=True)
class CPUCoreTopology:
    """Topology descriptor for Alder Lake i5-12450H."""
    p_core_indices: List[int]
    e_core_indices: List[int]
    total_logical: int
    total_physical: int


class AlderLakeAffinityScheduler:
    """
    Manages process and thread affinity across Intel Alder Lake P-cores and E-cores.
    """

    def __init__(self):
        self.process = psutil.Process()
        total_logical = psutil.cpu_count(logical=True) or 12
        total_physical = psutil.cpu_count(logical=False) or 8

        # On 12-thread i5-12450H:
        # P-cores are 0-7, E-cores are 8-11
        if total_logical >= 12:
            self.p_cores = list(range(0, 8))
            self.e_cores = list(range(8, 12))
        else:
            half = total_logical // 2
            self.p_cores = list(range(0, half))
            self.e_cores = list(range(half, total_logical))

        self.topology = CPUCoreTopology(
            p_core_indices=self.p_cores,
            e_core_indices=self.e_cores,
            total_logical=total_logical,
            total_physical=total_physical,
        )

    def get_current_affinity(self) -> List[int]:
        """Returns the current CPU affinity list of the process."""
        return self.process.cpu_affinity()

    def set_p_core_affinity(self):
        """Pins the current process exclusively to Performance-cores."""
        try:
            self.process.cpu_affinity(self.p_cores)
        except Exception:
            pass

    def set_e_core_affinity(self):
        """Pins the current process exclusively to Efficient-cores."""
        try:
            self.process.cpu_affinity(self.e_cores)
        except Exception:
            pass

    def reset_affinity(self):
        """Restores affinity across all available logical cores."""
        try:
            all_cores = list(range(self.topology.total_logical))
            self.process.cpu_affinity(all_cores)
        except Exception:
            pass

    @contextmanager
    def pin_p_cores(self) -> Generator[None, None, None]:
        """
        Context manager that temporarily locks execution to P-cores,
        restoring previous affinity on exit.
        """
        old_aff = self.get_current_affinity()
        try:
            self.set_p_core_affinity()
            yield
        finally:
            try:
                self.process.cpu_affinity(old_aff)
            except Exception:
                pass

    @contextmanager
    def pin_e_cores(self) -> Generator[None, None, None]:
        """
        Context manager that temporarily locks execution to E-cores,
        restoring previous affinity on exit.
        """
        old_aff = self.get_current_affinity()
        try:
            self.set_e_core_affinity()
            yield
        finally:
            try:
                self.process.cpu_affinity(old_aff)
            except Exception:
                pass

    def run_on_e_core_async(self, target: Callable, args: tuple = ()) -> threading.Thread:
        """
        Spawns a background worker thread pinned to E-cores for async telemetry.
        """
        def worker():
            with self.pin_e_cores():
                target(*args)

        t = threading.Thread(target=worker, daemon=True)
        t.start()
        return t
