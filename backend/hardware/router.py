"""
backend/hardware/router.py
Layer 1 — Silicon Awakening: Hardware-aware execution router.

Scores each available backend by expected tokens/sec for the current model
size and routes accordingly. Supports multi-target fan-out: splits a single
generation request across CPU + iGPU + NPU simultaneously using layer-wise
or tensor-split partitioning.
"""

from __future__ import annotations

import logging
from typing import Dict, Any, List, Optional

from backend.hardware.detector import HardwareDetector, HardwareProfile

logger = logging.getLogger(__name__)

# ── Backend scoring constants (relative tokens/sec multipliers vs CPU baseline) ──
_BACKEND_SCORE: Dict[str, float] = {
    "npu":       4.0,   # NPU: lowest power, fast for small models
    "metal":     3.5,   # Apple Silicon GPU (Metal)
    "mlx":       3.5,   # Apple MLX (uses Metal internally)
    "vulkan":    3.0,   # iGPU Vulkan (Intel Iris/Arc, AMD Radeon)
    "directml":  2.8,   # DirectML (Windows iGPU/NPU)
    "openvino":  2.5,   # OpenVINO (Intel CPU/iGPU/NPU)
    "cpu_amx":   2.2,   # Intel AMX (4th-gen Xeon / Core Ultra)
    "cpu_avx512_vnni": 1.9,
    "cpu_avx512": 1.6,
    "cpu_avx2":  1.3,
    "cpu_generic": 1.0,
    "cloud_api": 0.0,   # cost = 0 compute but latency penalty
}


class HeterogeneousRouter:
    """
    Decides where to route a workload based on hardware capabilities and task
    specifications.  Ensures NVIDIA-dependency is minimised by scheduling on
    CPU, iGPU, and NPU whenever possible.

    Key new capability vs previous version:
      - score_backends() returns an ordered list of (backend_name, score)
      - build_device_plan() creates a layer-partitioned device_plan dict that
        llama.cpp / OpenVINO / MLX can consume via --tensor-split / -ngl flags
    """

    def __init__(self, system_profile: Optional[HardwareProfile] = None):
        if system_profile is None:
            self.profile = HardwareDetector.get_system_profile()
        else:
            self.profile = system_profile
        logger.info("Heterogeneous Router initialized with system profile.")

    # ── Backend scoring ───────────────────────────────────────────────────────

    def score_backends(self) -> List[tuple[str, float]]:
        """Return ordered list of (backend_name, score) for available backends."""
        cpu = self.profile.cpu
        gpu = self.profile.igpu
        npu = self.profile.npu
        scores: Dict[str, float] = {}

        # iGPU / GPU backends
        if gpu.metal:
            scores["metal"] = _BACKEND_SCORE["metal"]
            scores["mlx"] = _BACKEND_SCORE["mlx"]
        if gpu.vulkan:
            scores["vulkan"] = _BACKEND_SCORE["vulkan"]
        if gpu.directml:
            scores["directml"] = _BACKEND_SCORE["directml"]
        if gpu.igpu_detected or gpu.vulkan or gpu.directml:
            scores["openvino"] = _BACKEND_SCORE["openvino"]

        # NPU backends
        if npu.has_npu:
            scores["npu"] = _BACKEND_SCORE["npu"]

        # CPU ISA-tiered backends
        if cpu.amx:
            scores["cpu_amx"] = _BACKEND_SCORE["cpu_amx"]
        if cpu.avx512_vnni:
            scores["cpu_avx512_vnni"] = _BACKEND_SCORE["cpu_avx512_vnni"]
        if cpu.avx512:
            scores["cpu_avx512"] = _BACKEND_SCORE["cpu_avx512"]
        if cpu.avx2 or cpu.neon:
            scores["cpu_avx2"] = _BACKEND_SCORE["cpu_avx2"]
        scores["cpu_generic"] = _BACKEND_SCORE["cpu_generic"]

        # Sort descending by score
        return sorted(scores.items(), key=lambda x: x[1], reverse=True)

    # ── Device plan (layer partitioning) ─────────────────────────────────────

    def build_device_plan(self, total_layers: int = 32) -> Dict[str, Any]:
        """
        Build a layer-partitioned device_plan for llama.cpp / OpenVINO.
        Returns: {
          "npu":  {"layers": N, "fraction": f},
          "igpu": {"layers": N, "fraction": f},
          "cpu":  {"layers": -1},           # remainder always on CPU
        }
        """
        gpu = self.profile.igpu
        npu = self.profile.npu
        ram_avail = self.profile.ram_available_gb

        plan: Dict[str, Any] = {}
        remaining = total_layers

        # NPU gets first N layers (small, fast, low power)
        if npu.has_npu:
            npu_layers = min(8, remaining // 4)
            plan["npu"] = {"layers": npu_layers, "fraction": round(npu_layers / total_layers, 3)}
            remaining -= npu_layers

        # iGPU gets the bulk of the middle layers (based on shared vram)
        if gpu.vulkan or gpu.directml or gpu.metal:
            vram_mb = gpu.vram_shared_mb
            # Rule of thumb: ~2 GB per 7B model INT4; scale proportionally
            # Cap at 75% of remaining layers
            igpu_cap = int(remaining * 0.75)
            if vram_mb >= 8000:
                igpu_layers = igpu_cap
            elif vram_mb >= 4000:
                igpu_layers = min(24, igpu_cap)
            elif vram_mb >= 2000:
                igpu_layers = min(16, igpu_cap)
            else:
                igpu_layers = min(8, igpu_cap)
            plan["igpu"] = {"layers": igpu_layers, "fraction": round(igpu_layers / total_layers, 3)}
            remaining -= igpu_layers

        # CPU gets whatever remains
        plan["cpu"] = {"layers": -1, "fraction": round(remaining / total_layers, 3)}
        return plan

    # ── Quantization selection ────────────────────────────────────────────────

    def select_quantization(self, task_type: str = "inference") -> str:
        """Pick lowest-bit quantization that fits in available RAM."""
        ram = self.profile.ram_available_gb
        cpu = self.profile.cpu

        if ram < 3.0:
            return "ternary"   # BitNet 1.58-bit
        if ram < 6.0:
            return "INT4"
        if ram < 10.0:
            return "INT8"
        return "FP16"

    # ── Main selection API (backward-compatible) ──────────────────────────────

    def select_backend(self, task_type: str, complexity_score: float = 0.5) -> Dict[str, Any]:
        """
        Determines the optimal execution backend for a task.
        Returns a decision dict consumed by universal_execution.py.
        """
        cpu = self.profile.cpu
        gpu = self.profile.igpu
        npu = self.profile.npu
        ram_available = self.profile.ram_available_gb

        decision: Dict[str, Any] = {
            "target": "CPU",
            "device_name": "Host Processor",
            "quantization": self.select_quantization(task_type),
            "thread_count": max(cpu.threads // 2, 2),
            "vram_allocated_gb": 0.0,
            "watts_predicted": 25.0,
            "strategy": "AVX2-Aligned",
            "device_plan": {},
            "backend_ranking": self.score_backends(),
        }

        # ── Symbolic tasks: always CPU ────────────────────────────────
        if task_type == "symbolic":
            decision["target"] = "CPU"
            decision["device_name"] = "CPU Core Array"
            decision["strategy"] = (
                "Single-threaded FSM/RETE" if complexity_score < 0.4
                else "Multi-threaded Constraint Solver"
            )
            decision["watts_predicted"] = 15.0 if complexity_score < 0.4 else 65.0
            return decision

        # ── Retrieval: always CPU ─────────────────────────────────────
        elif task_type == "retrieval":
            decision["target"] = "CPU"
            decision["device_name"] = "CPU Disk Thread Pool"
            decision["strategy"] = "Memory-mapped I/O Index"
            decision["watts_predicted"] = 20.0
            return decision

        # ── Embeddings: iGPU/NPU preferred ───────────────────────────
        elif task_type == "embeddings":
            if gpu.metal:
                decision.update({
                    "target": "iGPU",
                    "device_name": gpu.devices[0] if gpu.devices else "Apple GPU",
                    "strategy": "MLX-Metal-FP16",
                    "watts_predicted": 15.0,
                })
            elif gpu.vulkan or gpu.directml:
                decision.update({
                    "target": "iGPU",
                    "device_name": gpu.devices[0] if gpu.devices else "Integrated GPU",
                    "strategy": "Vulkan-FP16 Kernels" if gpu.vulkan else "DirectML-FP16",
                    "watts_predicted": 35.0,
                })
            elif npu.has_npu:
                decision.update({
                    "target": "NPU",
                    "device_name": npu.type,
                    "strategy": "NPU Tensor Acceleration",
                    "watts_predicted": 10.0,
                })
            else:
                decision.update({
                    "target": "CPU",
                    "strategy": "AVX2 Parallel Matrix" if cpu.avx2 else "CPU GEMM",
                    "watts_predicted": 45.0,
                })
            return decision

        # ── Inference: multi-target fan-out ──────────────────────────
        elif task_type == "inference":
            # Cloud escape valve: complex + RAM-starved
            if complexity_score > 0.85 and ram_available < 6.0:
                decision.update({
                    "target": "Cloud-API",
                    "device_name": "Frontier Cloud Fallback",
                    "quantization": "FP16-Server",
                    "strategy": "Secured Enclave Fallback",
                    "watts_predicted": 0.0,
                })
                return decision

            # Build layer-partitioned device_plan
            decision["device_plan"] = self.build_device_plan()

            # Primary device selection (highest score wins)
            ranking = self.score_backends()
            best_backend = ranking[0][0] if ranking else "cpu_generic"

            if best_backend in ("npu",) and complexity_score < 0.70:
                decision.update({
                    "target": "NPU",
                    "device_name": npu.type,
                    "watts_predicted": 8.0,
                    "strategy": f"NPU Ternary ({npu.api})",
                })
            elif best_backend in ("metal", "mlx"):
                decision.update({
                    "target": "iGPU",
                    "device_name": gpu.devices[0] if gpu.devices else "Apple GPU",
                    "watts_predicted": 18.0,
                    "strategy": "MLX Metal Inference",
                })
            elif best_backend in ("vulkan", "directml", "openvino"):
                decision.update({
                    "target": "iGPU",
                    "device_name": gpu.devices[0] if gpu.devices else "Integrated GPU",
                    "watts_predicted": 30.0,
                    "strategy": (
                        "Vulkan INT4 GGUF" if gpu.vulkan else
                        "DirectML INT4" if gpu.directml else
                        "OpenVINO INT4"
                    ),
                })
            elif best_backend == "cpu_amx":
                decision.update({
                    "target": "CPU",
                    "device_name": "CPU + Intel AMX",
                    "watts_predicted": 40.0,
                    "strategy": "AMX Ternary GEMM",
                })
            else:
                isa = "AVX512" if cpu.avx512 else "AVX2" if cpu.avx2 else "NEON" if cpu.neon else "generic"
                decision.update({
                    "target": "CPU",
                    "device_name": "CPU Array",
                    "watts_predicted": 55.0,
                    "strategy": f"CPU {decision['quantization']} ({isa})",
                })

            return decision

        return decision
