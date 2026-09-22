"""
hyper/discovery package
=======================
Universal Computational Transformation, Discovery & Equivalence Engine (UCTDE).
"""

from hyper.discovery.hypotheses import EpistemicState, UniversalityLevel, ResearchHypothesis, TargetStatus
from hyper.discovery.knowledge_graph import ComputationalKnowledgeGraph, NodeType, EdgeType
from hyper.discovery.proof_engine import ProofDiscoveryEngine, ProofCertificate, ProofStatus
from hyper.discovery.counterexample_engine import CounterexampleDiscoveryEngine, Counterexample, CounterexampleDatabase
from hyper.discovery.universality_ladder import UniversalityLadder, UniversalityBoundaryEngine, BoundaryReport
from hyper.discovery.meta_search import (
    MetaSearchEngine,
    SearchStrategyType,
    FormalBarrierClassifier,
    FormalBarrierType,
    AdaptiveSearchScaler,
)
from hyper.discovery.resource_transcendence import ResourceTranscendenceEngine, ResourceVector, TranscendenceVerdict
from hyper.discovery.self_critique import SelfCritiqueEngine, SelfCritiqueReport
from hyper.discovery.transformation_library import TransformationLibrary, TransformationRule
from hyper.discovery.loop import UniversalDiscoveryLoop, DiscoveryExperimentResult
from hyper.discovery.engine import UniversalComputationalDiscoveryEngine
from hyper.discovery.capability_registry import CapabilityRegistry, CapabilityEntry, MaturityLevel, FeatureStatus
from hyper.discovery.search_space_compiler import SearchSpaceCompiler, TransformationSearchSpace
from hyper.discovery.counterfactual_engine import CounterfactualEngine, CounterfactualHypothesis, CounterfactualType, PathwayCompositionGraph
from hyper.discovery.fairness_engine import BenchmarkFairnessEngine, FairnessReport, FairnessViolation
from hyper.discovery.alphatensor_engine import AlphaTensorEngine, BilinearTensorProblem, TensorAlgorithmCandidate
from hyper.discovery.alphaevolve_engine import AlphaEvolveEngine, ProgramIndividual, EvolutionaryRunResult
from hyper.discovery.runtime_hook import RuntimeDiscoveryHook, RuntimeOpportunity, RuntimeObservation
from hyper.discovery.discovery_experiments import DiscoveryExperimentSuite

from hyper.discovery.capability_decomposer import GPUCapabilityDecomposer, CapabilityFamily, CapabilityDetail
from hyper.discovery.workload_decomposer import WorkloadDecomposer, WorkloadDependencyGraph, WorkloadDecompositionResult
from hyper.discovery.pathway_ir import (
    PathwayIR,
    TransformationStep,
    ExecutionPlan,
    ExecutionDevice,
    MemoryPlan,
    MemoryStrategy,
    SchedulingPlan,
    SchedulingStrategy,
    VerificationPlan,
    FallbackPlan,
    PathwayCostEstimate,
)
from hyper.discovery.pathway_generator import PathwayGenerator
from hyper.discovery.pathway_composer import PathwayComposer, CompositionInteractionResult
from hyper.discovery.cost_model import PathwayCostModel, CostEvaluationResult, TimeBreakdown, ResourceProfile
from hyper.discovery.checkpoint_engine import CheckpointEngine, DiscoveryCheckpoint, CheckpointMetadata
from hyper.discovery.discovery_report import PathwayDiscoveryReport
from hyper.discovery.destination_tracker import DestinationTracker, ParityMetrics
from hyper.discovery.controlled_workloads import ControlledWorkloadBenchmark

__all__ = [
    "EpistemicState",
    "UniversalityLevel",
    "ResearchHypothesis",
    "TargetStatus",
    "ComputationalKnowledgeGraph",
    "NodeType",
    "EdgeType",
    "ProofDiscoveryEngine",
    "ProofCertificate",
    "ProofStatus",
    "CounterexampleDiscoveryEngine",
    "Counterexample",
    "CounterexampleDatabase",
    "UniversalityLadder",
    "UniversalityBoundaryEngine",
    "BoundaryReport",
    "MetaSearchEngine",
    "SearchStrategyType",
    "FormalBarrierClassifier",
    "FormalBarrierType",
    "AdaptiveSearchScaler",
    "ResourceTranscendenceEngine",
    "ResourceVector",
    "TranscendenceVerdict",
    "SelfCritiqueEngine",
    "SelfCritiqueReport",
    "TransformationLibrary",
    "TransformationRule",
    "UniversalDiscoveryLoop",
    "DiscoveryExperimentResult",
    "UniversalComputationalDiscoveryEngine",
    "CapabilityRegistry",
    "CapabilityEntry",
    "MaturityLevel",
    "FeatureStatus",
    "SearchSpaceCompiler",
    "TransformationSearchSpace",
    "CounterfactualEngine",
    "CounterfactualHypothesis",
    "CounterfactualType",
    "PathwayCompositionGraph",
    "BenchmarkFairnessEngine",
    "FairnessReport",
    "FairnessViolation",
    "AlphaTensorEngine",
    "BilinearTensorProblem",
    "TensorAlgorithmCandidate",
    "AlphaEvolveEngine",
    "ProgramIndividual",
    "EvolutionaryRunResult",
    "RuntimeDiscoveryHook",
    "RuntimeOpportunity",
    "RuntimeObservation",
    "DiscoveryExperimentSuite",
    "GPUCapabilityDecomposer",
    "CapabilityFamily",
    "CapabilityDetail",
    "WorkloadDecomposer",
    "WorkloadDependencyGraph",
    "WorkloadDecompositionResult",
    "PathwayIR",
    "TransformationStep",
    "ExecutionPlan",
    "ExecutionDevice",
    "MemoryPlan",
    "MemoryStrategy",
    "SchedulingPlan",
    "SchedulingStrategy",
    "VerificationPlan",
    "FallbackPlan",
    "PathwayCostEstimate",
    "PathwayGenerator",
    "PathwayComposer",
    "CompositionInteractionResult",
    "PathwayCostModel",
    "CostEvaluationResult",
    "TimeBreakdown",
    "ResourceProfile",
    "CheckpointEngine",
    "DiscoveryCheckpoint",
    "CheckpointMetadata",
    "PathwayDiscoveryReport",
    "DestinationTracker",
    "ParityMetrics",
    "ControlledWorkloadBenchmark",
]
