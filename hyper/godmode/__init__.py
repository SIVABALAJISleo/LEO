"""
hyper/godmode/__init__.py
=========================
HYPER-GODMODE: Universal Computational Pathway Discovery, Inverse Computation, Information Sufficiency, Counterfactual Optimization & Observable GPU Equivalence Engine.
"""

from .orchestrator.godmode_orchestrator import (
    GodmodeExecutionSummary,
    GodmodeOrchestrator,
)
from .pathway_evolution.evolution_engine import (
    GenerationSummary,
    EvolutionarySearchTrace,
    PathwayEvolutionEngine,
)
from .dashboard import (
    GodmodeDashboardMetrics,
    GodmodeDashboard,
    router as godmode_router,
)
from .godmode_omega import (
    godmode_omega_engine,
    HyperGodmodeOmegaEngine,
    GodmodeOmegaSuiteResult,
)
from .workload_contracts import (
    ContractRegistry,
    WorkloadContract,
    ExactnessRequirement,
    WorkloadFamily,
)
from .bottleneck_detector import (
    IntelligentBottleneckDetector,
    BottleneckClass,
    BottleneckReport,
    TelemetrySnapshot,
)
from .computation_elimination import (
    ComputationEliminationEngine,
    OptimizationCertificate,
)
from .memory_engine import (
    WorkingSetManager,
    BoundedBufferPool,
    ChunkedTilingEngine,
    MemoryBudget,
)
from .adaptive_scheduler import (
    AdaptiveHeterogeneousScheduler,
    ExecutionBackend,
    HardwareTopologyProfile,
)
from .playbooks import (
    BottleneckPlaybookRegistry,
    OptimizationPlaybook,
)
from .ai_inference import (
    AIInferenceOptimizer,
    KVCacheMemoryBudget,
    ModelInferenceProfile,
)
from .graphics_video import (
    GraphicsVideoOptimizer,
    CullingResult,
    DirtyRegionResult,
)
from .scientific_engine import (
    ScientificComputingOptimizer,
    SolverConvergenceCertificate,
    LowRankApproximationCertificate,
)

__all__ = [
    "GodmodeExecutionSummary",
    "GodmodeOrchestrator",
    "GenerationSummary",
    "EvolutionarySearchTrace",
    "PathwayEvolutionEngine",
    "GodmodeDashboardMetrics",
    "GodmodeDashboard",
    "godmode_router",
    "godmode_omega_engine",
    "HyperGodmodeOmegaEngine",
    "GodmodeOmegaSuiteResult",
    "ContractRegistry",
    "WorkloadContract",
    "ExactnessRequirement",
    "WorkloadFamily",
    "IntelligentBottleneckDetector",
    "BottleneckClass",
    "BottleneckReport",
    "TelemetrySnapshot",
    "ComputationEliminationEngine",
    "OptimizationCertificate",
    "WorkingSetManager",
    "BoundedBufferPool",
    "ChunkedTilingEngine",
    "MemoryBudget",
    "AdaptiveHeterogeneousScheduler",
    "ExecutionBackend",
    "HardwareTopologyProfile",
    "BottleneckPlaybookRegistry",
    "OptimizationPlaybook",
    "AIInferenceOptimizer",
    "KVCacheMemoryBudget",
    "ModelInferenceProfile",
    "GraphicsVideoOptimizer",
    "CullingResult",
    "DirtyRegionResult",
    "ScientificComputingOptimizer",
    "SolverConvergenceCertificate",
    "LowRankApproximationCertificate",
]

