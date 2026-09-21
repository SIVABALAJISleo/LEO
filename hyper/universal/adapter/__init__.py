"""
hyper/universal/adapter/__init__.py
===================================
Universal Workload Adapter package.
"""

from .workload_types import WorkloadDomain, WorkloadNecessityClass, InputOutputSchema
from .workload_adapter import UniversalWorkload, UniversalWorkloadAdapter

__all__ = [
    "WorkloadDomain",
    "WorkloadNecessityClass",
    "InputOutputSchema",
    "UniversalWorkload",
    "UniversalWorkloadAdapter",
]
