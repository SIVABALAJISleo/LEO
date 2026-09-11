"""
hyper_cco/hardware_advantage_analyzer.py
=============================================================================
Hardware Advantage Inversion & GADR/HAE Analyzer (Sections 18 & 19)
=============================================================================
Deconstructs why discrete GPUs outperform CPUs on brute-force workloads,
and calculates how software wormholes eliminate the application's need
for those specific hardware features.

Metrics:
  GADR (GPU Advantage Dependency Ratio):
      GADR = GPU-advantaged necessary work / original GPU-advantaged work

  HAE (Hardware Advantage Erasure):
      HAE = 1 - GADR

RULE:
HAE = 100% does NOT mean the CPU physically matches discrete GPU throughput.
It means the application's required observable has zero remaining dependency
on that GPU-specific architectural feature.
"""

from __future__ import annotations
import enum
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional


class GPUAdvantageType(str, enum.Enum):
    MASSIVE_PARALLELISM = "MASSIVE_PARALLELISM"       # 10k+ SIMT execution lanes
    HIGH_VRAM_BANDWIDTH = "HIGH_VRAM_BANDWIDTH"       # > 1000 GB/s GDDR6X/HBM3
    TENSOR_CORES = "TENSOR_CORES"                     # Dense 4x4 matrix MMA units
    RT_CORES = "RT_CORES"                             # Hardware BVH traversal & ray-box tests
    VRAM_CAPACITY = "VRAM_CAPACITY"                   # 24-80 GB dedicated onboard VRAM
    HIGH_POWER_ENVELOPE = "HIGH_POWER_ENVELOPE"       # 300W - 600W thermal dissipation
    HARDWARE_VIDEO_CODEC = "HARDWARE_VIDEO_CODEC"     # Dedicated NVENC/NVDEC silicon
    EXTREME_FP16_THROUGHPUT = "EXTREME_FP16_THROUGHPUT" # 2x packed FP16 vectorization


@dataclass
class HardwareAdvantageInversion:
    advantage_type: GPUAdvantageType
    why_gpu_wins: str
    software_inversion_strategy: str
    original_work_units: float
    remaining_work_units: float
    gadr: float
    hae: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "advantage_type": self.advantage_type.value,
            "why_gpu_wins": self.why_gpu_wins,
            "software_inversion_strategy": self.software_inversion_strategy,
            "original_work_units": self.original_work_units,
            "remaining_work_units": self.remaining_work_units,
            "gadr": round(self.gadr, 4),
            "hae_percentage": round(self.hae * 100.0, 2),
        }


class HardwareAdvantageAnalyzer:
    """Analyzes and calculates GPU Advantage Inversion for any workload."""

    INVERSION_STRATEGIES: Dict[GPUAdvantageType, Dict[str, str]] = {
        GPUAdvantageType.MASSIVE_PARALLELISM: {
            "why": "Computes millions of independent elements concurrently.",
            "strategy": "Spatio-Temporal Delta Bounding Boxes & Active Region Masks (compute only changed elements)."
        },
        GPUAdvantageType.HIGH_VRAM_BANDWIDTH: {
            "why": "Streams dense uncompressed arrays at > 1,000 GB/s without memory stalls.",
            "strategy": "Semantic Compression, INT8 Quantization, and Zero-Copy Shared USM Memory."
        },
        GPUAdvantageType.TENSOR_CORES: {
            "why": "Hardware systolic arrays execute dense GEMMs at extreme TFLOPS.",
            "strategy": "Low-Rank SVD Subspace Factorization, E-Graph Rewriting, and Exact State Memoization."
        },
        GPUAdvantageType.RT_CORES: {
            "why": "Dedicated hardware units accelerate BVH tree ray-triangle intersection tests.",
            "strategy": "Analytical Signed Distance Fields, Temporal Reprojection, and Bilateral Denoising."
        },
        GPUAdvantageType.HIGH_POWER_ENVELOPE: {
            "why": "Brute-forces billions of superfluous operations using 450W power draw.",
            "strategy": "Proof-Carrying Work Elimination (eliminates 70-99% of computation to fit 45W TDP)."
        },
        GPUAdvantageType.HARDWARE_VIDEO_CODEC: {
            "why": "Dedicated ASIC blocks encode and decode frames in fixed-function silicon.",
            "strategy": "Intel QuickSync integration + ROI Selective Decoding."
        },
        GPUAdvantageType.EXTREME_FP16_THROUGHPUT: {
            "why": "High-throughput half-precision vector execution units.",
            "strategy": "AVX2 CPU VNNI / OpenVINO INT8 quantized execution."
        },
    }

    @classmethod
    def evaluate_inversion(
        cls,
        advantage_type: GPUAdvantageType,
        original_work_units: float,
        remaining_necessary_units: float,
        custom_strategy: Optional[str] = None
    ) -> HardwareAdvantageInversion:
        original = max(1e-9, float(original_work_units))
        remaining = max(0.0, min(original, float(remaining_necessary_units)))
        gadr = remaining / original
        hae = 1.0 - gadr

        desc = cls.INVERSION_STRATEGIES.get(
            advantage_type,
            {"why": "Specialized accelerator hardware.", "strategy": "Algorithmic transformation."}
        )

        return HardwareAdvantageInversion(
            advantage_type=advantage_type,
            why_gpu_wins=desc["why"],
            software_inversion_strategy=custom_strategy or desc["strategy"],
            original_work_units=original,
            remaining_work_units=remaining,
            gadr=gadr,
            hae=hae
        )
