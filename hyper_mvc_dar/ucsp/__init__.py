"""
hyper_mvc_dar/ucsp
Universal Computation Subsumption Protocol (UCSP) & Holographic Compute Subsumption Engine (HCSE)
Autonomous 4-Tier Subsumption Architecture:
- Tier 0: Absolute Elimination (MinHash/SimHash Cuckoo Gatekeeper)
- Tier 1: The Leaf Engine (AVX2 vpshufb 4-bit LUT + iGPU Texture-Mapped KAN TMU)
- Tier 2: Reduced-Work Speculation (Freivalds' Probabilistic Verification)
- Tier 3: Heterogeneous Zero-Copy Fallback (OS-Level mmap Stream Dispatch)
"""

from .tier0_gatekeeper import SemanticGatekeeper
from .tier1_leaf_engine import (
    AVX2LUTEngine,
    TextureMappedKAN,
    subsumed_4bit_gemm_kernel,
    subsumed_4bit_matmul_kernel,
)
from .tier2_speculative_oracle import FreivaldsVerifier, SpeculativeOracle
from .tier3_zero_copy import ZeroCopyModelLoader, HeterogeneousZeroCopyDispatcher
from .coordinator import UCSPCoordinator

__all__ = [
    "SemanticGatekeeper",
    "AVX2LUTEngine",
    "TextureMappedKAN",
    "subsumed_4bit_gemm_kernel",
    "subsumed_4bit_matmul_kernel",
    "FreivaldsVerifier",
    "SpeculativeOracle",
    "ZeroCopyModelLoader",
    "HeterogeneousZeroCopyDispatcher",
    "UCSPCoordinator",
]
