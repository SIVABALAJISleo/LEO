"""
hyper/frontends/__init__.py
===========================
Universal Frontends Package for LEO/HYPER.
Exports FrontendRegistry, CIRFrontend, TensorGraphFrontend, CUDALikeFrontend,
OpenCLFrontend, SYCLFrontend, and SemanticNormalizer.
"""

from hyper.frontends.frontend_registry import (
    BaseFrontend,
    FrontendMetadata,
    FrontendRegistry,
    UnsupportedSemanticError,
)
from hyper.frontends.cir_frontend import CIRFrontend
from hyper.frontends.tensor_graph_frontend import TensorGraphFrontend
from hyper.frontends.cuda_frontend import CUDALikeFrontend
from hyper.frontends.opencl_frontend import OpenCLFrontend
from hyper.frontends.sycl_frontend import SYCLFrontend
from hyper.frontends.normalizer import SemanticNormalizer

# Register all built-in frontends
FrontendRegistry.register(CIRFrontend)
FrontendRegistry.register(TensorGraphFrontend)
FrontendRegistry.register(CUDALikeFrontend)
FrontendRegistry.register(OpenCLFrontend)
FrontendRegistry.register(SYCLFrontend)

__all__ = [
    "BaseFrontend",
    "FrontendMetadata",
    "FrontendRegistry",
    "UnsupportedSemanticError",
    "CIRFrontend",
    "TensorGraphFrontend",
    "CUDALikeFrontend",
    "OpenCLFrontend",
    "SYCLFrontend",
    "SemanticNormalizer",
]
