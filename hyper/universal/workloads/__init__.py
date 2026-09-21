"""
hyper/universal/workloads/__init__.py
=====================================
Universal Benchmark & Adversarial Workload Subsystem.
"""

from .suite import UniversalWorkloadSuite
from .adversarial import AdversarialWorkloadGenerator

__all__ = [
    "UniversalWorkloadSuite",
    "AdversarialWorkloadGenerator",
]
