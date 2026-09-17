"""
hyper/v8/__init__.py
====================
HYPER v8 — Necessary-Work Compiler + Contract Parity Engine.

Public surface:
    ComputeContractV2       - formal contract definition
    PathClassification      - execution path taxonomy
    NecessaryWorkGraph      - dependency DAG
    NecessaryWorkMap        - per-node necessity labels
    CheapestValidPathSelector
    ExactResidualEngine     - exact incremental computation
    HeterogeneousScheduler  - CPU + Intel UHD dynamic partitioning
    DeviceCertificate       - real device proof
    ExecutionCertificate    - per-result provenance
    BenchmarkHarnessV2      - provenance-complete benchmarking
    SelfFalsificationEngine - adversarial test generator
"""

from .contract import (
    ComputeContractV2,
    PathClassification,
    VerificationStatus,
    ContractValidator,
)
from .nwc import (
    NecessaryWorkGraph,
    NecessaryWorkMap,
    NecessityLabel,
    DependencyAnalyzer,
    ChangeDetectionEngine,
)
from .residual import ExactResidualEngine, ResidualProof
from .path_selector import CheapestValidPathSelector, ExecutionCertificate
from .scheduler import HeterogeneousSchedulerV2, DeviceCertificate
from .benchmark import BenchmarkHarnessV2, BenchmarkResult
from .falsification import SelfFalsificationEngine, FalsificationResult

__version__ = "8.0.0"

__all__ = [
    # Contract
    "ComputeContractV2",
    "PathClassification",
    "VerificationStatus",
    "ContractValidator",
    # NWC
    "NecessaryWorkGraph",
    "NecessaryWorkMap",
    "NecessityLabel",
    "DependencyAnalyzer",
    "ChangeDetectionEngine",
    # Residual
    "ExactResidualEngine",
    "ResidualProof",
    # Path selection
    "CheapestValidPathSelector",
    "ExecutionCertificate",
    # Scheduler
    "HeterogeneousSchedulerV2",
    "DeviceCertificate",
    # Benchmark
    "BenchmarkHarnessV2",
    "BenchmarkResult",
    # Falsification
    "SelfFalsificationEngine",
    "FalsificationResult",
    "__version__",
]
