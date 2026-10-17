"""
hyper_universal/craft/__init__.py
=================================
Specialized Computation Engines for the Tony Stark Computational Escape Engine.
Implements Section 10 of the Master Specification:
- ExactCraft: Exact arithmetic, modular, symbolic, and exact subproblem reuse.
- SparseCraft: Genuine sparsity detection, CSR execution, and 2:4 structured SIMD.
- StreamCraft: Out-of-core chunked streaming, bounded buffering, and cache tiling.
- TensorCraft: Fused operators (GEMM+Bias+ReLU), cache-aware loop blocking, OpenVINO IR.
- InferenceCraft: BitNet 1.58b ternary quantization, KV-cache, speculative decoding.
- DeviceCraft: Intel Core i5-12450H + Intel UHD iGPU runtime dispatch and latency gating.
"""

from hyper_universal.craft.exact_craft import ExactCraft
from hyper_universal.craft.sparse_craft import SparseCraft
from hyper_universal.craft.stream_craft import StreamCraft
from hyper_universal.craft.tensor_craft import TensorCraft
from hyper_universal.craft.inference_craft import InferenceCraft
from hyper_universal.craft.device_craft import DeviceCraft

__all__ = [
    "ExactCraft",
    "SparseCraft",
    "StreamCraft",
    "TensorCraft",
    "InferenceCraft",
    "DeviceCraft",
]
