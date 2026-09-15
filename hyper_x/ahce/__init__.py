"""
hyper_x/ahce/__init__.py
========================
Adaptive Hybrid Computation Elimination (AHCE) Engine Package.
"""

from .contract import AHCEContract, CorrectnessClass
from .candidate import AHCECandidate, AHCETrialResult
from .workload_signature import WorkloadSignature, StructuralFeatures
from .provenance import EvidenceProvenance, ProvenanceTag
from .evidence import AHCEEvidenceRecord, AHCETelemetryRecord
from .feature_extractor import AHCEFeatureExtractor
from .analyzer import AHCEWorkloadAnalyzer, AnalysisTelemetry
from .classifier import AHCEClassifier, WorkloadArchetype
from .strategy_registry import AHCEStrategyRegistry, AHCEStrategy
from .strategy_selector import AHCEStrategySelector
from .cost_model import AHCECostModel, CostBreakdown, WorkBreakdown
from .trial_executor import AHCETrialExecutor
from .parallel_trials import AHCEParallelTrialExecutor
from .evaluator import AHCECandidateEvaluator
from .verifier import AHCEVerifier, AHCEVerificationVerdict
from .falsifier import AHCEFalsifier, AHCEFalsificationResult
from .holdout import AHCEHoldoutEvaluator, AHCEHoldoutResult
from .learner import AHCEMetaLearner, StrategyExperience
from .telemetry import AHCETelemetryCollector
from .research_loop import AHCEResearchEngine, AHCEResearchVerdict
from .experiments import AHCEResearchSuite

__all__ = [
    "AHCEContract",
    "CorrectnessClass",
    "AHCECandidate",
    "AHCETrialResult",
    "WorkloadSignature",
    "StructuralFeatures",
    "EvidenceProvenance",
    "ProvenanceTag",
    "AHCEEvidenceRecord",
    "AHCETelemetryRecord",
    "AHCEFeatureExtractor",
    "AHCEWorkloadAnalyzer",
    "AnalysisTelemetry",
    "AHCEClassifier",
    "WorkloadArchetype",
    "AHCEStrategyRegistry",
    "AHCEStrategy",
    "AHCEStrategySelector",
    "AHCECostModel",
    "CostBreakdown",
    "WorkBreakdown",
    "AHCETrialExecutor",
    "AHCEParallelTrialExecutor",
    "AHCECandidateEvaluator",
    "AHCEVerifier",
    "AHCEVerificationVerdict",
    "AHCEFalsifier",
    "AHCEFalsificationResult",
    "AHCEHoldoutEvaluator",
    "AHCEHoldoutResult",
    "AHCEMetaLearner",
    "StrategyExperience",
    "AHCETelemetryCollector",
    "AHCEResearchEngine",
    "AHCEResearchVerdict",
    "AHCEResearchSuite",
]
