"""
LEO AI VInfinity – Optimization Fabric Integration Test Suite
============================================================
Verifies:
  1. Topological Hypergraph sorted binary lookup complexity, multi-hop traversal constraints, and memory limits.
  2. Predictive Delta Synthesis compression and Jaccard drift verification.
  3. Ternary weight accumulation and spiking sparse threshold activations.
  4. Speculative Agent Swarm proposals consensus and target accept validation.
  5. OpenVINO dispatch priorities and evolutionary parameter tuning.
  6. Telemetry and verification false-positive metrics.
"""

import pytest
import numpy as np
from backend.layers.v_infinity_orchestrator import (
    VInfinityOrchestrator,
    TopologicalHypergraph,
    PredictiveDeltaEngine,
    TernarySparseOptimization,
    SpeculativeSwarmEngine,
    SelfEvolvingOrchestrator
)

@pytest.fixture
def orchestrator():
    return VInfinityOrchestrator(latency_slo_ms=2500.0, confidence_floor=0.70)

class TestTopologicalHypergraph:
    def test_edge_addition_and_sorting(self):
        graph = TopologicalHypergraph()
        graph.add_edge("B", "C", "depends_on", 0.9)
        graph.add_edge("A", "C", "uses", 0.8)
        graph.add_edge("B", "A", "contains", 0.95)

        # Confirm elements are sorted by target node names
        edges_b = [e["target"] for e in graph.adj["B"]]
        assert edges_b == sorted(edges_b)

    def test_binary_search_edge(self):
        graph = TopologicalHypergraph()
        graph.add_edge("LEO", "OpenVINO", "runs", 0.9)
        graph.add_edge("LEO", "CPU", "uses", 0.95)
        graph.add_edge("LEO", "iGPU", "accelerates", 0.85)

        edge = graph.get_edge_binary("LEO", "iGPU")
        assert edge is not None
        assert edge["relation"] == "accelerates"
        assert edge["weight"] == 0.85

        # Check for missing edge
        missing = graph.get_edge_binary("LEO", "NPU")
        assert missing is None

    def test_multi_hop_traversal_budget(self):
        graph = TopologicalHypergraph()
        # Seed linear chain
        graph.add_edge("Node1", "Node2", "points", 0.9)
        graph.add_edge("Node2", "Node3", "points", 0.9)
        graph.add_edge("Node3", "Node4", "points", 0.9)

        # Traversal with large budget should find all
        facts_unlimited = graph.traverse_multi_hop(["Node1"], max_hops=3, memory_budget_bytes=1000)
        assert len(facts_unlimited) == 3

        # Traversal with restricted budget (e.g. 50 bytes) should stop early
        facts_limited = graph.traverse_multi_hop(["Node1"], max_hops=3, memory_budget_bytes=50)
        assert len(facts_limited) < 3
        assert len(facts_limited) > 0


class TestPredictiveDelta:
    def test_delta_synthesizer_jaccard(self):
        engine = PredictiveDeltaEngine()
        pred = "LEO optimization fabric runs local models with high efficiency."
        
        # Outcome is identical -> similarity should be 1.0 (avoided)
        is_valid, sim = engine.verify_delta(pred, pred)
        assert is_valid is True
        assert sim == 1.0

        # Outcome is highly similar -> Jaccard index >= 0.8
        similar_outcome = "LEO intelligence optimization fabric runs local models with high efficiency."
        is_valid2, sim2 = engine.verify_delta(pred, similar_outcome, tolerance=0.8)
        assert is_valid2 is True
        assert sim2 >= 0.8

        # Outcome is very different -> delta is large (not avoided)
        diff_outcome = "something else completely different and unrelated."
        is_valid3, sim3 = engine.verify_delta(pred, diff_outcome, tolerance=0.8)
        assert is_valid3 is False
        assert sim3 < 0.5


class TestTernarySparse:
    def test_ternary_quantization_emulation(self):
        weights = np.array([[1.8, 0.2, -0.9], [-0.1, 2.5, 0.0]])
        activations = np.array([1.0, 2.0, 3.0])
        
        res = TernarySparseOptimization.emulate_ternary_matmul(weights, activations)
        # Weights clamped to [[1, 0, -1], [0, 1, 0]]
        # Row 1: 1*1 + 0*2 + -1*3 = -2
        # Row 2: 0*1 + 1*2 + 0*3 = 2
        assert np.array_equal(res, np.array([-2.0, 2.0]))

    def test_spiking_sparse_activation(self):
        activations = np.array([0.1, 0.4, 0.05, 0.9])
        spiked = TernarySparseOptimization.spiking_sparse_activation(activations, threshold=0.25)
        # 0.1 and 0.05 should be zeroed
        # 0.4 and 0.9 should fire
        assert spiked[0] == 0.0
        assert spiked[2] == 0.0
        assert spiked[1] == 0.4
        assert spiked[3] == 0.9


class TestSpeculativeSwarms:
    def test_swarm_proposals(self):
        engine = SpeculativeSwarmEngine()
        props = engine.coordinate_swarm_proposal("CPU optimization")
        assert len(props) > 0
        assert "VInfinity" in props

    def test_speculative_verification_flow(self):
        engine = SpeculativeSwarmEngine()
        proposals = ["A", "B", "C", "D"]
        
        # Test repeat execution to verify avoidance rates
        for _ in range(5):
            rate, accepted = engine.run_speculative_verification(proposals)
            assert 0.0 <= rate <= 1.0
            assert len(accepted) <= len(proposals)

        pct = engine.get_avoidance_rate_pct()
        assert 0.0 <= pct <= 100.0


class TestSelfEvolvingRouter:
    def test_device_prioritization(self, orchestrator):
        router = SelfEvolvingOrchestrator(orchestrator)
        
        # If NPU + iGPU are active
        hw = {"has_igpu": True, "has_npu": True}
        devices = router.get_openvino_device_priority(hw)
        assert devices == ["NPU", "GPU", "CPU"]

        # Only CPU
        hw_cpu = {"has_igpu": False, "has_npu": False}
        devices_cpu = router.get_openvino_device_priority(hw_cpu)
        assert devices_cpu == ["CPU"]

    def test_evolutionary_parameter_mutator(self, orchestrator):
        router = SelfEvolvingOrchestrator(orchestrator)

        # Run multiple mutations
        for _ in range(5):
            mut = router.mutate_parameters()
            assert mut["generation"] > 0
            assert "fitness" in mut
            assert mut["status"] in ("APPLIED", "DISCARDED")

        # Config should mutate but remain within valid ranges
        assert 0.40 <= orchestrator.confidence_floor <= 0.90
        assert 500.0 <= orchestrator.latency_slo_ms <= 5000.0


class TestVInfinityOrchestratorFull:
    def test_full_workflow_execution(self, orchestrator):
        res = orchestrator.execute_semantic_workflow(
            "How does LEO optimize CPU and iGPU performance?", {}
        )
        assert "answer" in res
        assert "confidence" in res
        assert "latency_ms" in res
        assert res["version"] == "VInfinity"
        assert res["entropy_tier"] == "vinfinity_fabric"
        assert "verification" in res
        assert "false_positive_rate" in res["verification"]
        assert "evolution" in res

    def test_get_system_status_telemetry(self, orchestrator):
        # Run a query to populate telemetry arrays
        orchestrator.execute_semantic_workflow("Test query", {})
        
        status = orchestrator.get_system_status()
        assert status["status"] == "ACTIVE"
        assert status["version"] == "VInfinity"
        assert "telemetry" in status
        assert "false_positive_rate" in status["telemetry"]
        assert "false_negative_rate" in status["telemetry"]
        assert "alignment_score" in status["telemetry"]
