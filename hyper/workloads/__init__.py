"""
hyper/workloads/__init__.py
===========================
Canonical Workload Package for LEO/HYPER.
"""

from hyper.workloads.canonical_corpus import (
    CanonicalWorkloadCorpus,
    CanonicalWorkload,
)

__all__ = [
    "CanonicalWorkloadCorpus",
    "CanonicalWorkload",
]
