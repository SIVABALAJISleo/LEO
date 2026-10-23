"""
hyper/canonical/__init__.py
===========================
The Authoritative Canonical 15-Workload Verification & Optimization Engine.
"""

from hyper.canonical.workload_registry import (
    ExactnessClass,
    TensorSchema,
    CanonicalWorkloadContract,
    CanonicalWorkloadRegistry,
    CANONICAL_REGISTRY,
    CANONICAL_15_WORKLOAD_IDS,
)

__all__ = [
    "ExactnessClass",
    "TensorSchema",
    "CanonicalWorkloadContract",
    "CanonicalWorkloadRegistry",
    "CANONICAL_REGISTRY",
    "CANONICAL_15_WORKLOAD_IDS",
]
