import os
import psutil
import logging

logger = logging.getLogger("HyperCore.ThreadPinner")

class ThreadPinner:
    """
    Manages CPU core affinity (pinning) for threads and processes to minimize
    context switching and ensure cache locality.
    """
    def __init__(self):
        self.process = psutil.Process(os.getpid())
        
    def pin_to_cores(self, core_ids: list[int]):
        """
        Pins the current process to a specific list of core IDs.
        Works on Linux and Windows.
        """
        try:
            if hasattr(self.process, 'cpu_affinity'):
                self.process.cpu_affinity(core_ids)
                logger.info(f"Process pinned to cores: {core_ids}")
                return True
            else:
                logger.warning("CPU affinity not supported on this OS.")
                return False
        except Exception as e:
            logger.error(f"Failed to set CPU affinity: {e}")
            return False

    def pin_critical_execution(self, p_cores: list[int]):
        """
        Pin dense math operations to Performance cores.
        """
        return self.pin_to_cores(p_cores)
        
    def pin_background_tasks(self, e_cores: list[int]):
        """
        Pin speculative rendering, compression, or semantic replay caching to Efficiency cores.
        """
        if not e_cores:
            # Fallback if no E-cores exist
            return False
        return self.pin_to_cores(e_cores)
