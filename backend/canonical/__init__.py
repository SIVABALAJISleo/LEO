"""
backend/canonical
=================
Verified Canonical Functional Replacement Engine and Native Runtimes for Project LEO.
Platform: Intel Core i5-12450H (4P+4E, 12T) + Intel UHD Graphics 48-EU.
"""

from .functional_replacement_engine import (
    FunctionalReplacementEngine,
    CurSkeletonFactoringResult,
    OfflineTruncatedSVDResult,
    QuantizedBitPackingResult,
    OutOfCoreTileResult,
)
from .native_runtime_bridge import NativeRuntimeBridge
from .unseen_subsumption_extensions import (
    HodlrCurResult,
    hodlr_banded_cur_gemm,
    ContextualHotColdResult,
    ContextualHotColdFFN,
    contextual_hot_cold_ffn_step,
    RadixPrefixNode,
    RadixPrefixCache,
    L3CoalescedConcurrencyResult,
    benchmark_l3_coalesced_concurrency,
    MeZOInPlaceTrainer,
    RadianceCascadeResult,
    deterministic_radiance_cascade_2d,
)

__all__ = [
    "FunctionalReplacementEngine",
    "CurSkeletonFactoringResult",
    "OfflineTruncatedSVDResult",
    "QuantizedBitPackingResult",
    "OutOfCoreTileResult",
    "NativeRuntimeBridge",
    "HodlrCurResult",
    "hodlr_banded_cur_gemm",
    "ContextualHotColdResult",
    "ContextualHotColdFFN",
    "contextual_hot_cold_ffn_step",
    "RadixPrefixNode",
    "RadixPrefixCache",
    "L3CoalescedConcurrencyResult",
    "benchmark_l3_coalesced_concurrency",
    "MeZOInPlaceTrainer",
    "RadianceCascadeResult",
    "deterministic_radiance_cascade_2d",
]
