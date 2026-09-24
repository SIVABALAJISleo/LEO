"""
hyper_universal package
========================
LEO / HYPER Ω: Universal Computational Discovery, Escape, Verification & Proof Engine.
"""

from hyper_universal.types import (
    ResultState,
    MetricProvenance,
    CacheRegime,
    ReferenceType,
    ClaimStatus,
)
from hyper_universal.work_meter import WorkMeter, WorkMeasurementReport, MetricValue
from hyper_universal.reference_provenance import ReferenceProvenance, ReferenceProvenanceManager
from hyper_universal.contract_ir import ContractIR, ContractType, NumericalTolerance, ResourceLimits
from hyper_universal.workload import UniversalWorkload, WorkloadFamily
from hyper_universal.necessary_work import NecessaryWorkAnalyzer, NecessaryWorkReport, OperationDetail
from hyper_universal.candidate import Candidate, CandidateGenealogy, CandidateNoveltyMetrics
from hyper_universal.sandbox import SandboxExecutor, SandboxExecutionResult, inspect_source_code
from hyper_universal.verification_fortress import VerificationFortress, FortressVerificationReport
from hyper_universal.counterexamples import CounterexampleEngine, Counterexample
from hyper_universal.proof import FormalTheorem, TheoremProofStatus, UniverseCoverageReport, UniversalQuantifierEngine
from hyper_universal.claim_gate import UniversalClaimGate, UniversalClaimChecklist, UniversalClaimCertificate
from hyper_universal.parity_engine import ParityEngine, MultidimensionalParityReport, DimensionParity
from hyper_universal.adaptive_orchestrator import AdaptiveOrchestrator, ExecutionRouting, RoutingDecision
from hyper_universal.research_loop import UniversalResearchLoop, DiscoveryCycleArtifact

__all__ = [
    "ResultState",
    "MetricProvenance",
    "CacheRegime",
    "ReferenceType",
    "ClaimStatus",
    "WorkMeter",
    "WorkMeasurementReport",
    "MetricValue",
    "ReferenceProvenance",
    "ReferenceProvenanceManager",
    "ContractIR",
    "ContractType",
    "NumericalTolerance",
    "ResourceLimits",
    "UniversalWorkload",
    "WorkloadFamily",
    "NecessaryWorkAnalyzer",
    "NecessaryWorkReport",
    "OperationDetail",
    "Candidate",
    "CandidateGenealogy",
    "CandidateNoveltyMetrics",
    "SandboxExecutor",
    "SandboxExecutionResult",
    "inspect_source_code",
    "VerificationFortress",
    "FortressVerificationReport",
    "CounterexampleEngine",
    "Counterexample",
    "FormalTheorem",
    "TheoremProofStatus",
    "UniverseCoverageReport",
    "UniversalQuantifierEngine",
    "UniversalClaimGate",
    "UniversalClaimChecklist",
    "UniversalClaimCertificate",
    "ParityEngine",
    "MultidimensionalParityReport",
    "DimensionParity",
    "AdaptiveOrchestrator",
    "ExecutionRouting",
    "RoutingDecision",
    "UniversalResearchLoop",
    "DiscoveryCycleArtifact",
]
