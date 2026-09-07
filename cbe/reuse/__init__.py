"""
cbe/reuse: Computational reuse mechanisms across time, space, and lighting samples.
Includes motion-compensated temporal reprojection, ReSTIR reservoir sampling,
and spatiotemporal radiance caching.
"""

from .temporal_reuse import TemporalReuseEngine, ReprojectionResult
from .spatial_reuse import SpatialReuseEngine
from .reservoir import Reservoir, ReservoirSampler, SamplePayload
from .sample_reuse import SpatiotemporalSampleReuse
from .radiance_reuse import RadianceCache

__all__ = [
    "TemporalReuseEngine",
    "ReprojectionResult",
    "SpatialReuseEngine",
    "Reservoir",
    "ReservoirSampler",
    "SamplePayload",
    "SpatiotemporalSampleReuse",
    "RadianceCache",
]
