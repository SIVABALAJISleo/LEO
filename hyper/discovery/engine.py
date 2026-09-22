"""
hyper/discovery/engine.py
=========================
Master Facade: Universal Computational Transformation, Discovery & Equivalence Engine (UCTDE).

Provides the unified research API for autonomous algorithmic discovery,
formal proof investigation, counterexample generation, and knowledge graph persistence.
"""

from __future__ import annotations
from typing import Any, Callable, Dict, List, Optional
import numpy as np

from hyper.discovery.hypotheses import EpistemicState, ResearchHypothesis, TargetStatus
from hyper.discovery.knowledge_graph import ComputationalKnowledgeGraph
from hyper.discovery.proof_engine import ProofDiscoveryEngine, ProofCertificate
from hyper.discovery.counterexample_engine import CounterexampleDiscoveryEngine, Counterexample
from hyper.discovery.meta_search import MetaSearchEngine, SearchStrategyType
from hyper.discovery.resource_transcendence import ResourceTranscendenceEngine
from hyper.discovery.self_critique import SelfCritiqueEngine
from hyper.discovery.transformation_library import TransformationLibrary
from hyper.discovery.loop import UniversalDiscoveryLoop, DiscoveryExperimentResult


from hyper.discovery.capability_decomposer import GPUCapabilityDecomposer, CapabilityFamily
from hyper.discovery.workload_decomposer import WorkloadDecomposer, WorkloadDecompositionResult
from hyper.discovery.pathway_ir import PathwayIR
from hyper.discovery.pathway_generator import PathwayGenerator
from hyper.discovery.pathway_composer import PathwayComposer, CompositionInteractionResult
from hyper.discovery.cost_model import PathwayCostModel, CostEvaluationResult
from hyper.discovery.checkpoint_engine import CheckpointEngine, DiscoveryCheckpoint
from hyper.discovery.destination_tracker import DestinationTracker, ParityMetrics
from hyper.discovery.controlled_workloads import ControlledWorkloadBenchmark
from hyper.discovery.discovery_report import PathwayDiscoveryReport
from hyper.ai.kimi_k3_brain import KimiK3DiscoveryBrain, DebateSessionResult


class UniversalComputationalDiscoveryEngine:
    """
    UCTDE — Unified Computational Discovery Subsystem.
    """

    def __init__(self) -> None:
        self.knowledge_graph = ComputationalKnowledgeGraph()
        self.transformation_library = TransformationLibrary()
        self.proof_engine = ProofDiscoveryEngine()
        self.counterexample_engine = CounterexampleDiscoveryEngine()
        self.meta_search = MetaSearchEngine()
        self.transcendence_engine = ResourceTranscendenceEngine()
        self.critique_engine = SelfCritiqueEngine()
        self.capability_decomposer = GPUCapabilityDecomposer()
        self.workload_decomposer = WorkloadDecomposer()
        self.pathway_generator = PathwayGenerator()
        self.pathway_composer = PathwayComposer()
        self.cost_model = PathwayCostModel()
        self.checkpoint_engine = CheckpointEngine()
        self.destination_tracker = DestinationTracker()
        self.controlled_benchmarks = ControlledWorkloadBenchmark()
        self.k3_brain = KimiK3DiscoveryBrain()
        self.loop = UniversalDiscoveryLoop(
            knowledge_graph=self.knowledge_graph,
            transformation_library=self.transformation_library,
        )
        self.target_status = TargetStatus()

    def discover(
        self,
        workload_fn: Callable[[Any], Any],
        sample_input: Any,
        workload_name: str = "DiscoveredWorkload",
        domain_hint: Optional[str] = None,
        max_candidates: int = 15,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> DiscoveryExperimentResult:
        """Runs an end-to-end scientific discovery loop on a computational workload."""
        res = self.loop.execute_discovery(
            workload_fn=workload_fn,
            sample_input=sample_input,
            workload_name=workload_name,
            domain_hint=domain_hint,
            max_candidates=max_candidates,
            metadata=metadata,
        )
        # Update target status
        if res.is_verified:
            self.target_status.verified_workload_count += 1
        if res.counterexample_found:
            self.target_status.counterexample_count += 1
        if res.proof_status == "FORMALLY_PROVED":
            self.target_status.proofs_established_count += 1

        return res

    def prove_claim(self, claim_type: str, degree: int = 32) -> ProofCertificate:
        """Attempts formal symbolic proof using SymPy."""
        if claim_type == "polynomial_horner":
            return self.proof_engine.attempt_polynomial_horner_proof(degree=degree)
        elif claim_type == "matrix_associativity":
            return self.proof_engine.attempt_matrix_associativity_proof()
        else:
            return self.proof_engine.attempt_arbitrary_claim_proof(
                claim_desc=claim_type,
                assumptions=["Standard field arithmetic"],
            )

    def attack_callable(
        self,
        candidate_fn: Callable[[Any], Any],
        reference_fn: Callable[[Any], Any],
        domain: str,
        hypothesis_id: str = "hyp-ad-hoc",
    ) -> Optional[Counterexample]:
        """Runs adversarial counterexample gauntlet to attempt falsifying candidate."""
        return self.counterexample_engine.attack_pathway(
            candidate_callable=candidate_fn,
            reference_callable=reference_fn,
            domain=domain,
            hypothesis_id=hypothesis_id,
        )

    def get_hypotheses(self) -> List[Dict[str, Any]]:
        nodes = self.knowledge_graph.find_nodes_by_type(
            self.knowledge_graph.nodes[list(self.knowledge_graph.nodes.keys())[0]].node_type.__class__.HYPOTHESIS
        ) if self.knowledge_graph.nodes else []
        return [n.to_dict() for n in nodes]

    def get_counterexamples(self) -> List[Dict[str, Any]]:
        return [cx.to_dict() for cx in self.counterexample_engine.db.all()]

    def get_proofs(self) -> List[Dict[str, Any]]:
        return [p.to_dict() for p in self.proof_engine.proof_history]

    def get_rules(self) -> List[Dict[str, Any]]:
        return [r.to_dict() for r in self.transformation_library.all_rules()]

    def get_experiments(self) -> List[Dict[str, Any]]:
        return [e.to_dict() for e in self.loop.experiments]

    def get_knowledge_graph_summary(self) -> Dict[str, Any]:
        return self.knowledge_graph.to_dict()

    def get_target_status(self) -> Dict[str, Any]:
        return self.target_status.to_dict()

    def decompose_gpu_capability(self, capability_name: str, domain_hint: Optional[str] = None) -> Dict[str, Any]:
        return self.capability_decomposer.decompose(capability_name, domain_hint).model_dump()

    def decompose_workload_dag(self, workload_name: str, sample_input: Any) -> WorkloadDecompositionResult:
        return self.workload_decomposer.decompose_workload(workload_name, sample_input)

    def generate_pathway_candidates(self, workload_name: str, sample_input: Any, max_candidates: int = 10) -> List[PathwayIR]:
        return self.pathway_generator.generate_candidates(workload_name, sample_input, max_candidates=max_candidates)

    def evaluate_cost(self, pathway: PathwayIR, baseline_latency_ms: float = 10.0) -> CostEvaluationResult:
        return self.cost_model.evaluate_cost(pathway, baseline_latency_ms)

    def compose_pathways(self, pathway_a: PathwayIR, pathway_b: PathwayIR) -> CompositionInteractionResult:
        return self.pathway_composer.compose_pair(pathway_a, pathway_b)

    def run_k3_debate(self, workload_name: str) -> DebateSessionResult:
        contract = self.capability_decomposer.create_contract_for_capability(workload_name, workload_name)
        return self.k3_brain.conduct_adversarial_debate(workload_name, contract)

    def run_controlled_workloads(self) -> List[PathwayDiscoveryReport]:
        reports = self.controlled_benchmarks.run_all()
        # Update destination tracker
        verified_count = sum(1 for r in reports if r.status == "VERIFIED")
        exact_count = sum(1 for r in reports if r.exactness == "EXACT")
        avg_speedup = float(np.mean([r.speedup for r in reports])) if reports else 1.0
        self.destination_tracker.update_from_benchmark_results(
            workloads_total=len(reports),
            workloads_verified=verified_count,
            exact_matches=exact_count,
            apps_covered=len(reports),
            total_apps=12,
            avg_speedup_vs_gpu_target=avg_speedup,
        )
        return reports

    def get_destination_tracker_summary(self) -> Dict[str, Any]:
        return self.destination_tracker.get_summary()

