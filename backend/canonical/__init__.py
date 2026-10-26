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

__all__ = [
    "FunctionalReplacementEngine",
    "CurSkeletonFactoringResult",
    "OfflineTruncatedSVDResult",
    "QuantizedBitPackingResult",
    "OutOfCoreTileResult",
    "NativeRuntimeBridge",
]
