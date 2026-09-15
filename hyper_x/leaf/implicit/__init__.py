"""
hyper_x/leaf/implicit/__init__.py
=================================
Mathematical Implicit Resolution Package for LEAF.
"""

from .field import ImplicitField, PolynomialField
from .representation import FourierFeatureField, LowRankImplicitMatrix
from .encoder import ImplicitEncoder
from .decoder import ImplicitDecoder
from .query import ImplicitQueryEngine
from .error_bound import ErrorBoundVerifier, RepresentationError
from .lut_approximator import LUTApproximator, NeuralImplicitResolution

__all__ = [
    "ImplicitField",
    "PolynomialField",
    "FourierFeatureField",
    "LowRankImplicitMatrix",
    "ImplicitEncoder",
    "ImplicitDecoder",
    "ImplicitQueryEngine",
    "ErrorBoundVerifier",
    "RepresentationError",
    "LUTApproximator",
    "NeuralImplicitResolution",
]
