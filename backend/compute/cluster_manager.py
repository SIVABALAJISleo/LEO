import os

# Critical Performance Injections BEFORE NumPy/SciPy load
# This forces the compute libraries to use OpenBLAS / MKL with optimized thread limits
# This MUST be executed before importing any heavy math libraries

def inject_openblas_config(max_threads: int):
    os.environ['OMP_NUM_THREADS'] = str(max_threads)
    os.environ['OPENBLAS_NUM_THREADS'] = str(max_threads)
    os.environ['MKL_NUM_THREADS'] = str(max_threads)
    os.environ['VECLIB_MAXIMUM_THREADS'] = str(max_threads)
    os.environ['NUMEXPR_NUM_THREADS'] = str(max_threads)

import logging
import psutil
from concurrent.futures import ProcessPoolExecutor
import asyncio

from backend.core.hyper_config import config

logger = logging.getLogger(__name__)

# Apply thread limits globally to avoid physical core starvation
inject_openblas_config(config.MAX_WORKERS)

class ClusterManager:
    """
    Acts as a lightweight orchestrator in lie of heavier frameworks like Ray for single-node scaling.
    Manages process pools dynamically based on CPU utilization and prioritizes workloads.
    """
    def __init__(self):
        self.max_workers = config.MAX_WORKERS
        self.pool = ProcessPoolExecutor(max_workers=self.max_workers)
        logger.info(f"Initialized Cluster Manager with {self.max_workers} worker processes.")

    def optimize_affinity(self, process_id: int, physical_core_id: int):
        """
        Binds a specific process to a physical core to prevent OS jumping context switches.
        """
        try:
            p = psutil.Process(process_id)
            # Confine process to a specific physical core logic
            # This is specific to OS and platform availability
            if hasattr(p, 'cpu_affinity'):
                p.cpu_affinity([physical_core_id])
                logger.debug(f"Process {process_id} pinned to core {physical_core_id}")
        except Exception as e:
            logger.debug(f"Thread affinity locking unachievable: {e}")

    async def execute_task(self, func, *args, priority=1):
        """
        Submits a task to the process pool. 
        In a heavily loaded system, a queue layer here determines order.
        For now, simply dispatches via asyncio bridge.
        """
        loop = asyncio.get_event_loop()
        
        # In a fully fleshed out Phase 4 we'd push to a PriorityQueue here and pop off,
        # but Python's ProcessPoolExecutor handles basic queueing safely.
        try:
            return await loop.run_in_executor(self.pool, func, *args)
        except Exception as e:
            logger.error(f"Cluster execute failed: {e}")
            raise

cluster = ClusterManager()
