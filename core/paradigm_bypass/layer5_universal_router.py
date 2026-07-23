import logging

logger = logging.getLogger(__name__)

class CPU_SIMD_Backend:
    name = "CPU_SIMD"
    def is_available(self): return True
    def run(self, task): return f"[{self.name}] Executed via AVX2"

class CPU_Binary_Backend:
    name = "CPU_BINARY"
    def is_available(self): return True
    def run(self, task): return f"[{self.name}] Executed via POPCNT"

class Intel_iGPU_OpenCL_Backend:
    name = "INTEL_IGPU_OPENCL"
    def is_available(self):
        try:
            import pyopencl
            return True
        except ImportError:
            return False
    def run(self, task): return f"[{self.name}] Executed on EUs"

class DirectML_Backend:
    name = "DIRECTML"
    def is_available(self):
        try:
            import onnxruntime
            return 'DmlExecutionProvider' in onnxruntime.get_available_providers()
        except ImportError:
            return False
    def run(self, task): return f"[{self.name}] Executed via DirectML"

class UniversalComputeRouter:
    def __init__(self):
        self.backends = [
            CPU_Binary_Backend(),
            CPU_SIMD_Backend(),
            Intel_iGPU_OpenCL_Backend(),
            DirectML_Backend()
        ]
        self.available_backends = self.detect_backends()
        logger.info(f"Detected backends: {[b.name for b in self.available_backends]}")

    def detect_backends(self):
        return [b for b in self.backends if b.is_available()]

    def select_backend(self, task: dict):
        pref = task.get("backend_preference")
        if pref:
            for b in self.available_backends:
                if b.name.lower() == pref.lower():
                    return b
                    
        # Auto-routing based on task type
        ttype = task.get("type", "")
        if "binary" in ttype:
            return self.available_backends[0] # CPU_Binary is fastest for POPCNT
        if "dense" in ttype and len(self.available_backends) > 3:
            return self.available_backends[3] # DirectML
            
        return self.available_backends[1] # CPU SIMD fallback
