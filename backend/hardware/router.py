"""
backend/hardware/router.py
Hardware-aware execution router that determines the optimal compute backend
for symbolic reasoning, semantic retrieval, embeddings, compressed local inference, and API fallback.
"""
import logging
from typing import Dict, Any
from backend.hardware.detector import HardwareDetector

logger = logging.getLogger(__name__)

class HeterogeneousRouter:
    """
    Decides where to route a workload based on hardware capabilities and task specifications.
    Ensures NVIDIA-dependency is minimized by scheduling on CPU, iGPU, and NPU whenever possible.
    """

    def __init__(self, system_profile: Dict[str, Any] = None):
        self.profile = system_profile or HardwareDetector.get_system_profile()
        logger.info("Heterogeneous Router initialized with system profile.")

    def select_backend(self, task_type: str, complexity_score: float = 0.5) -> Dict[str, Any]:
        """
        Determines the optimal execution backend for a task.
        
        Task Types:
          - 'symbolic': Policy solvers, constraint programming, Prolog.
          - 'retrieval': BM25 keyword scans and document vector search indexing.
          - 'embeddings': Dense vector representations, similarity maps.
          - 'inference': LLM execution, generation, translation.
        
        Complexity Score:
          - 0.0 (trivial) to 1.0 (extremely heavy)
        """
        cpu = self.profile.get("cpu", {})
        gpu = self.profile.get("gpu", {})
        npu = self.profile.get("npu", {})
        ram = self.profile.get("ram", {})

        decision = {
            "target": "CPU",
            "device_name": "Host Processor",
            "quantization": "FP32",
            "thread_count": max(cpu.get("threads", 4) // 2, 2),
            "vram_allocated_gb": 0.0,
            "watts_predicted": 25.0,
            "strategy": "AVX2-Aligned"
        }

        # Rule 1: Symbolic tasks ALWAYS execute on CPU (high branch density, low matrix utility)
        if task_type == "symbolic":
            decision["target"] = "CPU"
            decision["device_name"] = "CPU Core Array"
            decision["strategy"] = "Single-threaded FSM/RETE" if complexity_score < 0.4 else "Multi-threaded Constraint Solver"
            decision["watts_predicted"] = 15.0 if complexity_score < 0.4 else 65.0
            return decision

        # Rule 2: Retrieval ALWAYS executes on CPU (mostly memory/disk bandwidth bound)
        elif task_type == "retrieval":
            decision["target"] = "CPU"
            decision["device_name"] = "CPU Disk Thread Pool"
            decision["strategy"] = "Memory-mapped I/O Index"
            decision["watts_predicted"] = 20.0
            return decision

        # Rule 3: Embedding computations go to iGPU or NPU if available, else fast CPU threads
        elif task_type == "embeddings":
            if gpu.get("vulkan") or gpu.get("directml") or gpu.get("metal"):
                decision["target"] = "iGPU"
                decision["device_name"] = gpu.get("devices", ["Integrated GPU"])[0]
                decision["strategy"] = "Vulkan-FP16 Kernels" if gpu.get("vulkan") else "DirectML-FP16"
                decision["watts_predicted"] = 35.0
            elif npu.get("has_npu"):
                decision["target"] = "NPU"
                decision["device_name"] = npu.get("type", "Ryzen AI / Intel NPU")
                decision["strategy"] = "NPU Tensor Acceleration"
                decision["watts_predicted"] = 10.0
            else:
                decision["target"] = "CPU"
                decision["strategy"] = "AVX2 Parallel Matrix"
                decision["watts_predicted"] = 45.0
            return decision

        # Rule 4: LLM Inference splits based on complexity and hardware
        elif task_type == "inference":
            # Extremely heavy, highly complex novel queries with high entropy go to cloud fallback if RAM is low
            if complexity_score > 0.85 and ram.get("available_gb", 16) < 6.0:
                decision["target"] = "Cloud-API"
                decision["device_name"] = "Frontier Cloud Fallback"
                decision["quantization"] = "FP16-Server"
                decision["strategy"] = "Secured Enclave Fallback"
                decision["watts_predicted"] = 0.0  # Zero local watt expenditure
                return decision

            # Local quantized low-bit models
            # Quantization level is determined by available memory and complexity
            if ram.get("available_gb", 16) < 4.0:
                decision["quantization"] = "INT2"
                decision["strategy"] = "Ultra-compressed Speculative (BitNet)"
            elif ram.get("available_gb", 16) < 8.0:
                decision["quantization"] = "INT4"
                decision["strategy"] = "4-bit Quantized GGUF"
            else:
                decision["quantization"] = "INT8"
                decision["strategy"] = "8-bit Quantized GGUF"

            # Route to NPU first for low power, then iGPU, then CPU
            if npu.get("has_npu") and complexity_score < 0.70:
                decision["target"] = "NPU"
                decision["device_name"] = npu.get("type", "Integrated NPU")
                decision["watts_predicted"] = 8.0
            elif gpu.get("vulkan") or gpu.get("directml") or gpu.get("metal"):
                decision["target"] = "iGPU"
                decision["device_name"] = gpu.get("devices", ["Integrated GPU"])[0]
                decision["watts_predicted"] = 30.0
            else:
                decision["target"] = "CPU"
                decision["device_name"] = "CPU Array"
                decision["watts_predicted"] = 55.0
                if cpu.get("avx512"):
                    decision["strategy"] += " (AVX512)"
                elif cpu.get("avx2"):
                    decision["strategy"] += " (AVX2)"
            
            return decision

        return decision
