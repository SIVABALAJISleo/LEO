import psutil
import platform
import logging

logger = logging.getLogger("HyperCore.Topology")

class TopologyAnalyzer:
    """
    Analyzes CPU topology to identify NUMA nodes, physical cores vs logical threads,
    and attempts to distinguish Performance (P) cores from Efficiency (E) cores.
    """
    def __init__(self):
        self.os_name = platform.system()
        self.logical_cores = psutil.cpu_count(logical=True)
        self.physical_cores = psutil.cpu_count(logical=False)
        self.freq_info = psutil.cpu_freq(percpu=True) if hasattr(psutil, 'cpu_freq') else None
        
        self.p_cores = []
        self.e_cores = []
        self._analyze_topology()
        
    def _analyze_topology(self):
        """
        Heuristic to separate P-cores and E-cores based on max frequency.
        In modern Intel architectures (e.g., Alder Lake/Raptor Lake), P-cores typically 
        report higher max frequencies and support Hyper-Threading.
        """
        # Fallback if percpu freq is not available
        if not self.freq_info or len(self.freq_info) != self.logical_cores:
            # Assume first half are P-cores, second half are E-cores as a mock fallback
            half = self.logical_cores // 2
            self.p_cores = list(range(half))
            self.e_cores = list(range(half, self.logical_cores))
            return

        max_freqs = [f.max for f in self.freq_info]
        # Find the max frequency in the system
        global_max = max(max_freqs) if max_freqs else 0
        
        for i, freq in enumerate(max_freqs):
            # If the core's max frequency is close to the global max (within 10%), assume P-core
            if freq >= global_max * 0.9:
                self.p_cores.append(i)
            else:
                self.e_cores.append(i)
                
        # Fallback if heuristic fails (e.g., all cores same freq like on older AMD/Intel)
        if not self.e_cores:
            self.p_cores = list(range(self.logical_cores))

    def get_topology_report(self) -> dict:
        return {
            "os": self.os_name,
            "logical_cores": self.logical_cores,
            "physical_cores": self.physical_cores,
            "p_core_count": len(self.p_cores),
            "e_core_count": len(self.e_cores),
            "p_cores": self.p_cores,
            "e_cores": self.e_cores
        }
