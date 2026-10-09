"""
hyper/parity_engine/__init__.py
===============================
HYPER 100% — Universal Computational / Functional / Application Parity Engine.

Master Mission:
«ACHIEVE 100% VERIFIED NON-PHYSICAL PARITY WITH THE COMPLETE EXTERNALLY OBSERVABLE
FUNCTIONAL, COMPUTATIONAL, APPLICATION, AND CONTRACT CAPABILITIES REQUIRED FROM
EXTERNAL GPU HARDWARE.»

Explicit Exclusion:
Physical hardware parity (transistors, CUDA cores, RT cores, physical VRAM chips, silicon)
is strictly OUT OF SCOPE.
"""

from .capability_registry import (
    CapabilityRegistry,
    GPUCapability,
    GPUDomain,
    CapabilityStatus,
)
from .contract_engine import (
    ContractEngine,
    ParityLevel,
    EquivalenceClass,
    PrecisionRequirement,
    ContractStatus,
    PerformanceContract,
    WorkloadContract,
)
from .pathway_ir import (
    PathwayIR,
    TargetDevicePlacement,
    TransformationRecord,
    TransformationType,
    MemoryPlan,
    SchedulerPlan,
    VerificationPlan,
    FallbackPlan,
)
from .workload_decomposer import (
    WorkloadDecomposer,
    SubOperation,
    NecessityAnalysis,
    DecomposedWorkload,
)
from .counterfactual_engine import (
    CounterfactualEngine,
    CounterfactualType,
    CounterfactualHypothesis,
    CounterfactualResult,
)
from .search_compiler import (
    SearchSpaceCompiler,
    SearchStrategy,
    SearchProgress,
)
from .kimi_k3_brain import (
    KimiK3DiscoveryBrain,
    K3SpecialistRole,
    K3ResearchProposal,
)
from .certificate_engine import (
    CertificateEngine,
    CertificateType,
    CertificateStatus,
    Certificate,
)
from .verification_engine import (
    VerificationEngine,
    EvidenceLevel,
    AntiCheatVerdict,
    VerificationRecord,
)
from .adversarial_engine import (
    AdversarialVerificationEngine,
    AdversarialCategory,
    AdversarialTestCase,
    AdversarialReport,
)
from .heterogeneous_engine import (
    HeterogeneousScheduler,
    MemoryPathwayEngine,
    HardwareTelemetry,
    MemoryOptimizationMetrics,
)
from .pathway_composer import (
    PathwayComposer,
    ComposedPathwayResult,
)
from .knowledge_graph import (
    DiscoveryKnowledgeGraph,
    FailureRecord,
    DiscoveryNode,
    DiscoveryEdge,
)
from .breakthrough_holdout import (
    BreakthroughHoldoutEngine,
    CrossDomainTransferRule,
    BlindHoldoutBenchmark,
    GeneralizationScoreCard,
)
from .application_parity import (
    UniversalApplicationParityHarness,
    ApplicationTarget,
    ApplicationValidationReport,
)
from .parity_score import (
    ParityScoreEngine,
    CapabilityScoreCard,
    GlobalParityScore,
    Section46PathwayReport,
)
from .autonomous_loop import (
    HyperUniversalPathwayEngine,
    CycleExecutionSummary,
)
from .first_experiments import (
    FirstAutomatedExperiments,
    ExperimentSuiteResult,
)
from .performance_engine import (
    PerformanceParityEngine,
    DetailedPerformanceMetrics,
    PerformanceParityVerdict,
)
from .sustained_performance import (
    SustainedPerformanceEngine,
    SustainedStabilityReport,
    SustainedTelemetrySample,
)
from .performance_discovery import (
    PerformanceDiscoveryMode,
    BreakthroughAttempt,
)
from .dashboard import (
    ParityDashboard,
    DashboardMetrics,
    router as dashboard_router,
)

__all__ = [
    "CapabilityRegistry",
    "GPUCapability",
    "GPUDomain",
    "CapabilityStatus",
    "ContractEngine",
    "ParityLevel",
    "EquivalenceClass",
    "PrecisionRequirement",
    "ContractStatus",
    "PerformanceContract",
    "WorkloadContract",
    "PathwayIR",
    "TargetDevicePlacement",
    "TransformationRecord",
    "TransformationType",
    "MemoryPlan",
    "SchedulerPlan",
    "VerificationPlan",
    "FallbackPlan",
    "WorkloadDecomposer",
    "SubOperation",
    "NecessityAnalysis",
    "DecomposedWorkload",
    "CounterfactualEngine",
    "CounterfactualType",
    "CounterfactualHypothesis",
    "CounterfactualResult",
    "SearchSpaceCompiler",
    "SearchStrategy",
    "SearchProgress",
    "KimiK3DiscoveryBrain",
    "K3SpecialistRole",
    "K3ResearchProposal",
    "CertificateEngine",
    "CertificateType",
    "CertificateStatus",
    "Certificate",
    "VerificationEngine",
    "EvidenceLevel",
    "AntiCheatVerdict",
    "VerificationRecord",
    "AdversarialVerificationEngine",
    "AdversarialCategory",
    "AdversarialTestCase",
    "AdversarialReport",
    "HeterogeneousScheduler",
    "MemoryPathwayEngine",
    "HardwareTelemetry",
    "MemoryOptimizationMetrics",
    "PathwayComposer",
    "ComposedPathwayResult",
    "DiscoveryKnowledgeGraph",
    "FailureRecord",
    "DiscoveryNode",
    "DiscoveryEdge",
    "BreakthroughHoldoutEngine",
    "CrossDomainTransferRule",
    "BlindHoldoutBenchmark",
    "GeneralizationScoreCard",
    "UniversalApplicationParityHarness",
    "ApplicationTarget",
    "ApplicationValidationReport",
    "ParityScoreEngine",
    "CapabilityScoreCard",
    "GlobalParityScore",
    "Section46PathwayReport",
    "HyperUniversalPathwayEngine",
    "CycleExecutionSummary",
    "FirstAutomatedExperiments",
    "ExperimentSuiteResult",
    "PerformanceParityEngine",
    "DetailedPerformanceMetrics",
    "PerformanceParityVerdict",
    "SustainedPerformanceEngine",
    "SustainedStabilityReport",
    "SustainedTelemetrySample",
    "PerformanceDiscoveryMode",
    "BreakthroughAttempt",
    "ParityDashboard",
    "DashboardMetrics",
    "dashboard_router",
]
