import logging
from typing import Any, Callable

from .topology_analyzer import TopologyAnalyzer
from .thread_pinner import ThreadPinner
from .cache_aware_tiling import CacheAwareTiler

logger = logging.getLogger("HyperCore.KernelScheduler")

class CPUKernelOrchestrator:
    """
    HyperCore MODULE 8 — CPU Kernel Orchestrator
    
    Dynamically schedules workloads to exploit the CPU optimally.
    - Pins dense execution paths to P-cores.
    - Pins async/compression paths to E-cores.
    - Uses cache-aware tiling to minimize DRAM round-trips.
    """
    def __init__(self):
        self.topology = TopologyAnalyzer()
        self.pinner = ThreadPinner()
        # Initialize tiler based on typical modern L2 cache sizes
        self.tiler = CacheAwareTiler(l2_cache_size_kb=1280) # Raptor Lake L2 is ~1.25MB - 2MB per core
        
        self.topology_report = self.topology.get_topology_report()
        logger.info(f"CPUKernelOrchestrator initialized on {self.topology_report['os']} "
                    f"with {self.topology_report['p_core_count']} P-Cores and {self.topology_report['e_core_count']} E-Cores.")

    def execute_dense_kernel(self, operation: Callable, *args, **kwargs) -> Any:
        """
        Executes a dense math operation pinned to P-Cores.
        """
        # Pin to P-cores
        if self.topology_report['p_cores']:
            self.pinner.pin_critical_execution(self.topology_report['p_cores'])
            
        # Execute the heavy operation
        result = operation(*args, **kwargs)
        
        # Unpin (allow OS scheduling again) - simulating cross-platform unpin by pinning to all cores
        all_cores = list(range(self.topology_report['logical_cores']))
        self.pinner.pin_to_cores(all_cores)
        
        return result

    def execute_background_task(self, task: Callable, *args, **kwargs) -> Any:
        """
        Executes a background task (e.g. semantic cache indexing, compression) pinned to E-Cores.
        """
        if self.topology_report['e_cores']:
            self.pinner.pin_background_tasks(self.topology_report['e_cores'])
        else:
            # Fallback if no E-cores
            logger.debug("No E-cores detected, falling back to OS scheduling.")
            
        result = task(*args, **kwargs)
        
        all_cores = list(range(self.topology_report['logical_cores']))
        self.pinner.pin_to_cores(all_cores)
        
        return result
        
    def run_tiled_matmul(self, A, B):
        """
        Executes a Cache-Oblivious Tiled Matrix Multiplication.
        """
        # We execute this heavy kernel on P-cores
        def _tiled_op():
            return self.tiler.tile_matrix_multiply(A, B)
            
        return self.execute_dense_kernel(_tiled_op)
