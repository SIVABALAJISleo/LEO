"""
backend/caoe/__init__.py
========================
CONTRACT-AWARE OPTIMIZATION ENGINE (CAOE) for LEO / HYPER.

Public Surface:
    ContractAwareOptimizationEngine - Main orchestrator
    ContractAnalyzer                - Workload analysis & tolerance sweep
    PrecisionReducer                - FP32/FP16/INT8 precision negotiation
    SparsityDetector                - Structural, temporal, and low-rank redundancy
    CacheManager                    - LRU smart caching with TTL & memory cap
    CPUiGPUScheduler                - Workload classifier & CPU/iGPU dispatcher
    Verifier                        - Absolute, relative, perceptual & functional verification
    TelemetryLayer                  - Real-time execution metrics & parity tracking
"""

from .contract_analyzer import ContractAnalyzer, WorkloadSpec, Contract
from .precision_reducer import PrecisionReducer
from .sparsity_detector import SparsityDetector
from .cache_manager import CacheManager
from .cpu_igpu_scheduler import CPUiGPUScheduler
from .verifier import Verifier, VerificationResult
from .telemetry import TelemetryLayer
from .caoe_engine import ContractAwareOptimizationEngine
from .intent_router import IntentLayer_v2, IntentClassification

__all__ = [
    "ContractAwareOptimizationEngine",
    "ContractAnalyzer",
    "WorkloadSpec",
    "Contract",
    "PrecisionReducer",
    "SparsityDetector",
    "CacheManager",
    "CPUiGPUScheduler",
    "Verifier",
    "VerificationResult",
    "TelemetryLayer",
    "IntentLayer_v2",
    "IntentClassification",
]
