"""
hyper_x/wormhole_compiler/__init__.py
=============================================================================
HYPER-X Computational Wormhole Compiler Package
=============================================================================
Autonomous Information-Boundary & Computational Wormhole Compiler.
"""

from hyper_x.wormhole_compiler.schemas import (
    WorkloadContract,
    ObservableRequirement,
    CorrectnessRequirement,
    CachePolicy,
    ExecutionTrack,
    NecessityClass,
    MutationType,
    RepresentationType,
    GrammarOperator,
    ProofClass,
    FailureCategory,
    PowerTelemetryType,
    CandidateAlgorithmRecord,
    CostVector,
    ProofRecord,
)

from hyper_x.wormhole_compiler.contract import ContractCompiler, ContractViolationError
from hyper_x.wormhole_compiler.observable import ObservableCompiler, ObservableExtractor
from hyper_x.wormhole_compiler.dependency_graph import InformationDependencyGraph
from hyper_x.wormhole_compiler.counterfactual import CounterfactualEngine
from hyper_x.wormhole_compiler.representation_space import RepresentationSpace
from hyper_x.wormhole_compiler.algorithm_grammar import AlgorithmGrammar, CompositeAlgorithm
from hyper_x.wormhole_compiler.egraph_search import EqualitySaturationEngine, EGraphRewriteRule
from hyper_x.wormhole_compiler.evolution_engine import EvolutionEngine, EvolutionaryIndividual
from hyper_x.wormhole_compiler.cost_model import HardwareCostModel
from hyper_x.wormhole_compiler.hardware_advantage_map import HardwareAdvantageMap
from hyper_x.wormhole_compiler.execution_fabric import ExecutionFabric, CapabilityProbe
from hyper_x.wormhole_compiler.patterns import WormholePatterns
from hyper_x.wormhole_compiler.learned_shortcuts import LearnedShortcutEngine
from hyper_x.wormhole_compiler.proof import MultiClassProofEngine
from hyper_x.wormhole_compiler.falsifier import AdversarialFalsifier, FalsificationResult
from hyper_x.wormhole_compiler.holdout import BlindHoldoutSystem, SealedHoldoutWorkload
from hyper_x.wormhole_compiler.candidate_registry import CandidateRegistry, FailureRecord
from hyper_x.wormhole_compiler.parity_gates import ParityEvaluator, StrictParityScorecard
from hyper_x.wormhole_compiler.domain_adapters import (
    MatrixMultiplicationAdapter,
    GraphicsTemporalAdapter,
    OutputSensitiveTopKAdapter,
    ScientificStencilAdapter,
    RAGEmbeddingRetrievalAdapter,
)
from hyper_x.wormhole_compiler.telemetry import (
    TelemetryCollector,
    ClaimValidationEngine,
    DualTrackScorer,
    ResearchCapabilityScorecard,
    HardwareParityScorecard,
)
from hyper_x.wormhole_compiler.compiler import WormholeCompiler
from hyper_x.wormhole_compiler.research_loop import (
    AutonomousResearchLoop,
    ResearchLoopReport,
    ResearchIteration,
)
from hyper_x.wormhole_compiler.information_boundary import InformationBoundaryEngine, BoundaryAnalysisResult
from hyper_x.wormhole_compiler.representation_inventor import RepresentationInventor, HybridRepresentationSpec
from hyper_x.wormhole_compiler.algorithm_genome import AlgorithmGenome
from hyper_x.wormhole_compiler.algorithm_mutator import AlgorithmMutator
from hyper_x.wormhole_compiler.algorithm_crossover import AlgorithmCrossover
from hyper_x.wormhole_compiler.counterexample import Counterexample
from hyper_x.wormhole_compiler.synthesis import CEGISSynthesizer
from hyper_x.wormhole_compiler.adversarial_generator import AdversarialGenerator
from hyper_x.wormhole_compiler.hardware_model import EmpiricalHardwareModel, HardwareExecutionProfile
from hyper_x.wormhole_compiler.compiler_backend import CompilerBackend
from hyper_x.wormhole_compiler.cpu_backend import CPUBackend
from hyper_x.wormhole_compiler.igpu_backend import IGPUBackend
from hyper_x.wormhole_compiler.hybrid_backend import HybridBackend
from hyper_x.wormhole_compiler.ir import HyperIRModule, IRTensor, IROperation
from hyper_x.wormhole_compiler.transfer_learning import CrossWorkloadTransferEngine, StructuralPrinciple
from hyper_x.wormhole_compiler.meta_search import MetaSearchEngine
from hyper_x.wormhole_compiler.knowledge_base import AlgorithmKnowledgeGraph, KnowledgeEntry
from hyper_x.wormhole_compiler.verifier import MultiVerifierSystem, MultiVerifierConsensus
from hyper_x.wormhole_compiler.provenance import ProvenanceTracker, ProvenanceRecord
from hyper_x.wormhole_compiler.claim_validator import ClaimValidator, ClaimAuditResult, ClaimStatus
from hyper_x.wormhole_compiler.experiment import ExperimentManager, ExperimentBudget

__all__ = [
    "WorkloadContract",
    "ObservableRequirement",
    "CorrectnessRequirement",
    "CachePolicy",
    "ExecutionTrack",
    "NecessityClass",
    "MutationType",
    "RepresentationType",
    "GrammarOperator",
    "ProofClass",
    "FailureCategory",
    "PowerTelemetryType",
    "CandidateAlgorithmRecord",
    "CostVector",
    "ProofRecord",
    "ContractCompiler",
    "ContractViolationError",
    "ObservableCompiler",
    "ObservableExtractor",
    "InformationDependencyGraph",
    "CounterfactualEngine",
    "RepresentationSpace",
    "AlgorithmGrammar",
    "CompositeAlgorithm",
    "EqualitySaturationEngine",
    "EGraphRewriteRule",
    "EvolutionEngine",
    "EvolutionaryIndividual",
    "HardwareCostModel",
    "HardwareAdvantageMap",
    "ExecutionFabric",
    "CapabilityProbe",
    "WormholePatterns",
    "LearnedShortcutEngine",
    "MultiClassProofEngine",
    "AdversarialFalsifier",
    "FalsificationResult",
    "BlindHoldoutSystem",
    "SealedHoldoutWorkload",
    "CandidateRegistry",
    "FailureRecord",
    "ParityEvaluator",
    "StrictParityScorecard",
    "MatrixMultiplicationAdapter",
    "GraphicsTemporalAdapter",
    "OutputSensitiveTopKAdapter",
    "ScientificStencilAdapter",
    "RAGEmbeddingRetrievalAdapter",
    "TelemetryCollector",
    "ClaimValidationEngine",
    "WormholeCompiler",
    "AutonomousResearchLoop",
    "ResearchLoopReport",
    "ResearchIteration",
    "InformationBoundaryEngine",
    "BoundaryAnalysisResult",
    "RepresentationInventor",
    "HybridRepresentationSpec",
    "AlgorithmGenome",
    "AlgorithmMutator",
    "AlgorithmCrossover",
    "Counterexample",
    "CEGISSynthesizer",
    "AdversarialGenerator",
    "EmpiricalHardwareModel",
    "HardwareExecutionProfile",
    "CompilerBackend",
    "CPUBackend",
    "IGPUBackend",
    "HybridBackend",
    "HyperIRModule",
    "IRTensor",
    "IROperation",
    "CrossWorkloadTransferEngine",
    "StructuralPrinciple",
    "MetaSearchEngine",
    "AlgorithmKnowledgeGraph",
    "KnowledgeEntry",
    "MultiVerifierSystem",
    "MultiVerifierConsensus",
    "ProvenanceTracker",
    "ProvenanceRecord",
    "ClaimValidator",
    "ClaimAuditResult",
    "ClaimStatus",
    "ExperimentManager",
    "ExperimentBudget",
    "DualTrackScorer",
    "ResearchCapabilityScorecard",
    "HardwareParityScorecard",
]
