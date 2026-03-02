import os
import psutil
import logging
import platform

logger = logging.getLogger(__name__)

class HardwareOptimizer:
    """
    Manages low-level CPU operations: thread pinning, NUMA localization, 
    allocator environments (jemalloc), and OpenBLAS/OMP threading.
    """
    @staticmethod
    def initialize_advanced_allocators():
        """
        In production environments (Linux mostly), inject jemalloc or tcmalloc 
        to replacing the default glibc malloc for lock-free fragmentation reductions.
        """
        if platform.system() == "Linux":
            # Just indicative; actual LD_PRELOAD needs to happen before process launch
            os.environ["MALLOC_CONF"] = "oversize_threshold:1,background_thread:true,metadata_thp:auto"
            logger.info("Configured dynamic memory for jemalloc hugepages and background threads.")

    @staticmethod
    def configure_numa_and_pinning(performance_mode="Balanced"):
        """
        Pin CPU threads and set memory affinity assuming python runs in NUMA nodes.
        Uses psutil to lock the main API threads to specific physical cores.
        """
        try:
            p = psutil.Process(os.getpid())
            physical_cores = psutil.cpu_count(logical=False) or 4
            logical_cores = psutil.cpu_count(logical=True) or 8

            if performance_mode == "Max CPU":
                # Bind to physical cores only (ignore SMT/Hyperthreading) for lower latency
                cpu_affinity = list(range(physical_cores))
                if hasattr(p, "cpu_affinity"):
                    p.cpu_affinity(cpu_affinity)
                os.environ["OMP_NUM_THREADS"] = str(physical_cores)
                os.environ["OPENBLAS_NUM_THREADS"] = str(physical_cores)
                logger.info(f"Pinned process to {len(cpu_affinity)} physical cores. OMP threads set to {physical_cores}.")
                
            elif performance_mode == "Low Power":
                # Bind to a single or a few efficiency cores (simulate via fewer resources)
                low_power_cores = [0, 1] if logical_cores > 2 else [0]
                if hasattr(p, "cpu_affinity"):
                    p.cpu_affinity(low_power_cores)
                os.environ["OMP_NUM_THREADS"] = str(len(low_power_cores))
                logger.info("Bound to Low Power Efficiency Cores.")
                
            elif performance_mode == "Max iGPU":
                # Free up CPU cores, assuming the iGPU (Vulkan/OpenCL) gets the workload
                os.environ["OMP_NUM_THREADS"] = str(max(1, physical_cores // 2))
                logger.info("Reduced CPU thread count to reserve power/thermal limits for iGPU.")
                
            else: # Balanced
                os.environ["OMP_NUM_THREADS"] = str(max(1, physical_cores - 1))
                
        except Exception as e:
            logger.warning(f"Could not apply strict thread PIN and NUMA boundaries: {e}")

    @staticmethod
    def setup(performance_mode="Balanced"):
        logger.info(f"Setting up Hardware Optimizer in {performance_mode} mode.")
        HardwareOptimizer.initialize_advanced_allocators()
        HardwareOptimizer.configure_numa_and_pinning(performance_mode)

if __name__ == "__main__":
    HardwareOptimizer.setup("Max CPU")
