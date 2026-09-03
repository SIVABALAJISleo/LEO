"""
hyper_v3/ir/operation.py
Operation types, exactness categories, and execution device targets for Universal IR.
"""

from enum import Enum


class OpType(Enum):
    MATMUL = "matmul"
    CONV2D = "conv2d"
    FFT = "fft"
    REDUCTION = "reduction"
    ATTENTION = "attention"
    ELEMENTWISE = "elementwise"
    ACTIVATION = "activation"
    MEMORY_TRANSFER = "memory_transfer"
    RAY_TRACE = "ray_trace"
    NBODY_FORCE = "nbody_force"
    MONTE_CARLO_SAMPLE = "monte_carlo_sample"
    SPARSE_TRANSFORM = "sparse_transform"
    FUSED_KERNEL = "fused_kernel"
    CUSTOM = "custom"


class DeviceType(Enum):
    CPU = "CPU"
    IGPU = "iGPU"
    HYBRID = "HYBRID"
    UNSPECIFIED = "UNSPECIFIED"


class NecessityStatus(Enum):
    MANDATORY = "MANDATORY"
    REDUNDANT = "REDUNDANT"
    REUSABLE = "REUSABLE"
    DERIVABLE = "DERIVABLE"
    ELIMINABLE = "ELIMINABLE"
    TRANSFORMABLE = "TRANSFORMABLE"
    APPROXIMABLE = "APPROXIMABLE"
    PREDICTABLE = "PREDICTABLE"
    UNKNOWN = "UNKNOWN"
