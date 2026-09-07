"""
cbe/scheduling: Adaptive resolution scaling, Variable Rate Shading (VRS),
sparse computation dispatch, and CPU+iGPU execution scheduling.
"""

from .adaptive_resolution import AdaptiveResolutionController, ResolutionTier
from .variable_rate import VariableRateShading, ShadingRate
from .sparse_scheduler import SparseTileScheduler
from .execution_scheduler import ExecutionScheduler

__all__ = [
    "AdaptiveResolutionController",
    "ResolutionTier",
    "VariableRateShading",
    "ShadingRate",
    "SparseTileScheduler",
    "ExecutionScheduler",
]
