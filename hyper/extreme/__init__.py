"""
hyper/extreme/__init__.py
=========================
Extreme Software-Only Heterogeneous Parity & Breakthrough Optimization Suite.

Modules:
- tbiqs: Tile-Based In-Cache Quantized Streaming (2-bit/4-bit packed codebooks, <9.6MB L3 resident)
- opencl_uva: Zero-Copy Unified Virtual Addressing via OpenCL on Intel UHD Graphics (48 EUs)
- lut_arithmetic: Bit-Level Arithmetic Morphing & Work-Group Local LUT Lookups
- cdre: Contract-Driven Redundancy Elimination Framework with strict drift detection (<10^-4)
- affinity_scheduler: Alder Lake Core Affinity Pinning Scheduler (P-cores 0-7, E-cores 8-11)
"""

from .tbiqs import TBIQSEngine, QuantizedTensor, L3_WORKING_SET_CEILING_BYTES
from .opencl_uva import OpenCLZeroCopyUVA
from .lut_arithmetic import LUTArithmeticEngine, MorphingLUT
from .cdre import CDREFramework, CDRETelemetry
from .affinity_scheduler import AlderLakeAffinityScheduler, CPUCoreTopology

__all__ = [
    "TBIQSEngine",
    "QuantizedTensor",
    "L3_WORKING_SET_CEILING_BYTES",
    "OpenCLZeroCopyUVA",
    "LUTArithmeticEngine",
    "MorphingLUT",
    "CDREFramework",
    "CDRETelemetry",
    "AlderLakeAffinityScheduler",
    "CPUCoreTopology",
]
