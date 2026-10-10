"""
hyper/hyper100_parity/__init__.py
==================================
HYPER 100% — Universal Computational / Functional / Application Parity Engine.

Master package exports:
- Universal GPU Capability Taxonomy & Registry (Sections 1-4)
- Performance Contract Engine (Section 28)
- Pathway IR (Section 8)
- GPU Capability & Workload Decomposer (Section 5)
- Counterfactual, Information-Sufficiency & Work Elimination Engine (Sections 10-15)
- Search Space Compiler (Sections 6, 8, 9)
- Kimi K3 Discovery Brain with 14 research roles (Section 7)
- Certificate Engine (Section 25)
- Trusted Reference & Verification Fortress (Sections 27, 32, 33)
- Adversarial Testing Gauntlet (Section 26)
- CPU+iGPU Heterogeneous Scheduler (Sections 23, 24)
- Pathway Composer (Section 35)
- Knowledge Graph, Failure Learning & Cross-Domain Discovery (Sections 36-38)
- Blind Holdout Mode & Generalization Score (Sections 40, 41)
- Universal Application Parity (Section 29)
- 100% Parity Score Engine & Global Coverage Matrix (Sections 30, 31, 46)
- Hyper Master Engine (Sections 49, 50)
- First Automated Experiment Runner (Section 48)
- Live Parity Dashboard (Section 45)
"""

from .taxonomy import (
    ParityLevel,
    CapabilityFamily,
    EquivalenceClass,
    EvidenceLevel,
    CapabilityEntry,
    UniversalCapabilityRegistry,
    GLOBAL_CAPABILITY_REGISTRY,
)
from .contract_engine import (
    ContractStatus,
    PrecisionMode,
    PerformanceContract,
)
from .pathway_ir import (
    DevicePlacement,
    DataRepresentation,
    MemoryStrategy,
    SchedulingStrategy,
    TransformationRecord,
    EstimatedCost,
    PathwayIR,
)
from .workload_decomposer import (
    TenQuestionsAnalysis,
    DAGNode,
    WorkloadDAG,
    DecompositionResult,
    GPUCapabilityDecomposer,
)
from .counterfactual_engine import (
    WorkClassification,
    CounterfactualHypothesis,
    InformationSufficiencyReport,
    WorkEliminationLedger,
    ReuseMemoEngine,
    CounterfactualEngine,
)
from .k3_brain import (
    K3ResearchRole,
    K3ResearchProposal,
    MultiAgentDebateSession,
    KimiK3DiscoveryBrain,
)
from .search_compiler import (
    SearchStrategyType,
    SearchSpaceLedger,
    SearchSpaceCompiler,
)
from .certificate_engine import (
    CertificateType,
    CertificateStatus,
    VerificationCertificate,
    CertificateEngine,
)
from .verification_engine import (
    NumericalErrorProfile,
    VerificationResult,
    TrustedReferenceEngine,
    IndependentVerifier,
)
from .adversarial_engine import (
    AdversarialTestResult,
    AdversarialGauntlet,
)
from .heterogeneous_compiler import (
    HardwareProfile,
    HeterogeneousDecision,
    HeterogeneousCompiler,
)
from .pathway_composer import (
    CompositionResult,
    PathwayComposer,
)
from .knowledge_graph import (
    FailureRecord,
    CrossDomainTransfer,
    DiscoveryKnowledgeGraph,
)
from .blind_holdout import (
    HoldoutWorkloadSpec,
    GeneralizationScoreReport,
    BlindHoldoutRunner,
)
from .application_parity import (
    ApplicationTarget,
    AppValidationRecord,
    ApplicationParityValidator,
)
from .score_engine import (
    CapabilityParityScore,
    GlobalCoverageMatrix,
    PathwayReport,
    ParityScoreEngine,
)
from .master_engine import (
    MasterPipelineExecutionResult,
    HyperMasterEngine,
)
from .first_experiment import (
    FirstExperimentResult,
    FirstAutomatedExperimentRunner,
)
from .dashboard import (
    generate_dashboard_html,
    router as parity_dashboard_router,
)

__all__ = [
    "ParityLevel",
    "CapabilityFamily",
    "EquivalenceClass",
    "EvidenceLevel",
    "CapabilityEntry",
    "UniversalCapabilityRegistry",
    "GLOBAL_CAPABILITY_REGISTRY",
    "ContractStatus",
    "PrecisionMode",
    "PerformanceContract",
    "DevicePlacement",
    "DataRepresentation",
    "MemoryStrategy",
    "SchedulingStrategy",
    "TransformationRecord",
    "EstimatedCost",
    "PathwayIR",
    "TenQuestionsAnalysis",
    "DAGNode",
    "WorkloadDAG",
    "DecompositionResult",
    "GPUCapabilityDecomposer",
    "WorkClassification",
    "CounterfactualHypothesis",
    "InformationSufficiencyReport",
    "WorkEliminationLedger",
    "ReuseMemoEngine",
    "CounterfactualEngine",
    "K3ResearchRole",
    "K3ResearchProposal",
    "MultiAgentDebateSession",
    "KimiK3DiscoveryBrain",
    "SearchStrategyType",
    "SearchSpaceLedger",
    "SearchSpaceCompiler",
    "CertificateType",
    "CertificateStatus",
    "VerificationCertificate",
    "CertificateEngine",
    "NumericalErrorProfile",
    "VerificationResult",
    "TrustedReferenceEngine",
    "IndependentVerifier",
    "AdversarialTestResult",
    "AdversarialGauntlet",
    "HardwareProfile",
    "HeterogeneousDecision",
    "HeterogeneousCompiler",
    "CompositionResult",
    "PathwayComposer",
    "FailureRecord",
    "CrossDomainTransfer",
    "DiscoveryKnowledgeGraph",
    "HoldoutWorkloadSpec",
    "GeneralizationScoreReport",
    "BlindHoldoutRunner",
    "ApplicationTarget",
    "AppValidationRecord",
    "ApplicationParityValidator",
    "CapabilityParityScore",
    "GlobalCoverageMatrix",
    "PathwayReport",
    "ParityScoreEngine",
    "MasterPipelineExecutionResult",
    "HyperMasterEngine",
    "FirstExperimentResult",
    "FirstAutomatedExperimentRunner",
    "generate_dashboard_html",
    "parity_dashboard_router",
]
