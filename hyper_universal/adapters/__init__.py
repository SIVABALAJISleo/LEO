"""
hyper_universal.adapters package
"""
from hyper_universal.adapters.adapter_registry import (
    WorkloadAdapter,
    DenseLinearAlgebraAdapter,
    SparseLinearAlgebraAdapter,
    SpectralFFTAdapter,
    AIInferenceAdapter,
    ImageProcessingAdapter,
    CompressionAdapter,
    CryptographyAdapter,
    PhysicsSimulationAdapter,
    SortingAndAlgorithmsAdapter,
    ProvisionalContractInferenceEngine,
    AdapterRegistry,
)

__all__ = [
    "WorkloadAdapter",
    "DenseLinearAlgebraAdapter",
    "SparseLinearAlgebraAdapter",
    "SpectralFFTAdapter",
    "AIInferenceAdapter",
    "ImageProcessingAdapter",
    "CompressionAdapter",
    "CryptographyAdapter",
    "PhysicsSimulationAdapter",
    "SortingAndAlgorithmsAdapter",
    "ProvisionalContractInferenceEngine",
    "AdapterRegistry",
]
