"""
hyper/core/__init__.py
Authoritative Core of LEO / HYPER:
Evidence-first, proof-carrying computational escape, formal verification,
and adaptive execution platform.
"""
from hyper.core.contract.models import ParityLevel, ContractType, SemanticContract
from hyper.core.semantic_ir.models import CanonicalSemanticIR, SemanticNode, SemanticOpCode, DeviceTarget
from hyper.core.obligation.analyzer import ComputationalObligationAnalyzer, ObligationAnalysisReport, OutputDirectedSlicer
from hyper.core.dependency.analyzer import DataDependencyGraph, DependencyEdge
from hyper.core.cost.ledger import WorkLedger, EndToEndCostModel, AccountingType
from hyper.core.evidence.models import EvidenceObject, EvidenceGrade, HardwareFingerprint
from hyper.core.evidence.truth_gate import TruthGate, GateDecision, TruthGateChecklist
from hyper.core.proof.engine import ProofEngine, ProofCertificate, ProofStatus
from hyper.core.verification.verifier import IndependentVerifier, AdversarialCounterexampleHunter, VerificationResult
from hyper.core.fallback.engine import CanonicalFallbackEngine, FallbackEvent
from hyper.core.scheduling.scheduler import AdaptiveDeviceScheduler, SchedulingClass
from hyper.core.pipeline import AuthoritativePipeline, PipelineExecutionResult

__all__ = [
    "ParityLevel",
    "ContractType",
    "SemanticContract",
    "CanonicalSemanticIR",
    "SemanticNode",
    "SemanticOpCode",
    "DeviceTarget",
    "ComputationalObligationAnalyzer",
    "ObligationAnalysisReport",
    "OutputDirectedSlicer",
    "DataDependencyGraph",
    "DependencyEdge",
    "WorkLedger",
    "EndToEndCostModel",
    "AccountingType",
    "EvidenceObject",
    "EvidenceGrade",
    "HardwareFingerprint",
    "TruthGate",
    "GateDecision",
    "TruthGateChecklist",
    "ProofEngine",
    "ProofCertificate",
    "ProofStatus",
    "IndependentVerifier",
    "AdversarialCounterexampleHunter",
    "VerificationResult",
    "CanonicalFallbackEngine",
    "FallbackEvent",
    "AdaptiveDeviceScheduler",
    "SchedulingClass",
    "AuthoritativePipeline",
    "PipelineExecutionResult",
]
