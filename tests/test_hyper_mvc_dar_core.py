"""
tests/test_hyper_mvc_dar_core.py
Unit tests for HYPER MVC-DAR Core: IR, Contracts, Information Sufficiency,
Necessity, Redundancy, Dead-Work Elimination, and Exact Transformations.
"""

import pytest
import numpy as np
from hyper_mvc_dar import (
    ComputationGraph,
    OpNode,
    OpType,
    TensorDescriptor,
    DataType,
    ExecutionContract,
    ContractClass,
    ExecutionTrack,
    InformationSufficiencyEngine,
    NecessityProofEngine,
    NecessityStatus,
    RedundancyEngine,
    DeadWorkEliminator,
    ExactTransformationEngine,
    ComplexityReplacementEngine,
    SparsityEngine,
    LowRankEngine,
    RepresentationDiscoveryEngine,
    RepresentationType,
    PrecisionEngine,
    MemoryEngine,
    HeterogeneousFabric,
    ErrorBudgetTracker,
)


def test_ir_graph_construction_and_toposort():
    graph = ComputationGraph("test_pipeline")
    t1 = TensorDescriptor("T1", (1024, 1024), DataType.FP32)
    t2 = TensorDescriptor("T2", (1024, 1024), DataType.FP32)
    t3 = TensorDescriptor("T3", (1024, 1024), DataType.FP32)
    t4 = TensorDescriptor("T4", (1024, 1024), DataType.FP32)

    graph.add_tensor(t1)
    graph.add_tensor(t2)
    graph.add_tensor(t3)
    graph.add_tensor(t4)

    node1 = OpNode("node1", OpType.MATMUL, ["T1", "T2"], ["T3"], estimated_flops=2 * (1024 ** 3))
    node2 = OpNode("node2", OpType.ACTIVATION, ["T3"], ["T4"], estimated_flops=1024 * 1024)

    graph.add_node(node1)
    graph.add_node(node2)
    graph.entry_inputs = ["T1", "T2"]
    graph.terminal_outputs = ["T4"]

    sorted_nodes = graph.topological_sort()
    assert len(sorted_nodes) == 2
    assert sorted_nodes[0].node_id == "node1"
    assert sorted_nodes[1].node_id == "node2"
    assert graph.total_estimated_flops() > 0


def test_information_sufficiency_and_dead_work():
    graph = ComputationGraph("dead_work_pipeline")
    t1 = TensorDescriptor("T1", (512, 512), DataType.FP32)
    t_live = TensorDescriptor("T_live", (512, 512), DataType.FP32)
    t_dead = TensorDescriptor("T_dead", (512, 512), DataType.FP32)

    graph.add_tensor(t1)
    graph.add_tensor(t_live)
    graph.add_tensor(t_dead)

    node_live = OpNode("node_live", OpType.ELEMENTWISE, ["T1"], ["T_live"], estimated_flops=1000)
    node_dead = OpNode("node_dead", OpType.ELEMENTWISE, ["T1"], ["T_dead"], estimated_flops=5000)

    graph.add_node(node_live)
    graph.add_node(node_dead)
    graph.terminal_outputs = ["T_live"]

    contract = ExecutionContract()
    suff = InformationSufficiencyEngine.analyze_graph(graph, contract)
    assert suff["essential_node_count"] == 1
    assert suff["discardable_node_count"] == 1

    elim_res = DeadWorkEliminator.eliminate_dead_work(graph)
    assert elim_res["eliminated_node_count"] == 1
    assert "node_dead" in elim_res["eliminated_nodes"]
    assert "node_dead" not in graph.nodes
    assert "node_live" in graph.nodes


def test_necessity_engine_classification():
    graph = ComputationGraph("necessity_pipeline")
    t1 = TensorDescriptor("T1", (256, 256), DataType.FP32)
    t2 = TensorDescriptor("T2", (256, 256), DataType.FP32)
    graph.add_tensor(t1)
    graph.add_tensor(t2)

    node_live = OpNode("live", OpType.MATMUL, ["T1"], ["T2"])
    graph.add_node(node_live)
    graph.terminal_outputs = ["T2"]

    contract = ExecutionContract()
    classif = NecessityProofEngine.classify_operation(node_live, graph, contract)
    assert classif["status"] == NecessityStatus.ESSENTIAL
    assert classif["can_eliminate"] is False


def test_redundancy_subexpression_cache():
    cache = RedundancyEngine(max_cache_entries=10)
    key = cache.compute_subexpression_hash("matmul", ("hash_a", "hash_b"), {"alpha": 1.0})
    
    assert cache.lookup(key) is None
    cache.store(key, "cached_matrix_result")
    assert cache.lookup(key) == "cached_matrix_result"
    assert cache.hit_rate > 0.0


def test_exact_transforms_and_operator_fusion():
    graph = ComputationGraph("fusion_test")
    t1 = TensorDescriptor("T1", (128, 128), DataType.FP32)
    t2 = TensorDescriptor("T2", (128, 128), DataType.FP32)
    t3 = TensorDescriptor("T3", (128, 128), DataType.FP32)
    graph.add_tensor(t1)
    graph.add_tensor(t2)
    graph.add_tensor(t3)

    n1 = OpNode("matmul1", OpType.MATMUL, ["T1"], ["T2"])
    n2 = OpNode("relu1", OpType.ACTIVATION, ["T2"], ["T3"])
    graph.add_node(n1)
    graph.add_node(n2)

    res = ExactTransformationEngine.apply_operator_fusion(graph)
    assert res["fused_count"] == 1
    assert "matmul1" in graph.nodes
    assert "relu1" not in graph.nodes
    assert graph.nodes["matmul1"].metadata.get("fused_activation") == "activation"


def test_complexity_replacement_nbody_and_fft():
    contract_exact = ExecutionContract(contract_class=ContractClass.EXACT)
    contract_approx = ExecutionContract(contract_class=ContractClass.NUMERICALLY_BOUNDED, relative_error=0.01)

    # N-Body
    rep_exact = ComplexityReplacementEngine.evaluate_n_body_replacement(2048, contract_exact)
    assert rep_exact["should_replace"] is False

    rep_approx = ComplexityReplacementEngine.evaluate_n_body_replacement(2048, contract_approx)
    assert rep_approx["should_replace"] is True
    assert rep_approx["asymptotic_speedup"] > 1.0

    # FFT
    rep_fft = ComplexityReplacementEngine.evaluate_fft_replacement(1024, 32, contract_approx)
    assert rep_fft["should_replace"] is True
    assert rep_fft["speedup"] > 1.0


def test_sparsity_and_low_rank_engines():
    # Sparsity
    dense_mat = np.zeros((100, 100))
    dense_mat[0, 0] = 5.0
    sp = SparsityEngine.measure_sparsity(dense_mat)
    assert sp > 0.95
    use_sparse, strat = SparsityEngine.should_use_sparse_format(dense_mat)
    assert use_sparse is True

    # Low-Rank
    u = np.random.randn(256, 16)
    v = np.random.randn(16, 256)
    low_rank_mat = u @ v
    eigenspec = LowRankEngine.analyze_eigenspectrum(low_rank_mat, tolerance=0.01)
    assert eigenspec["is_low_rank"] is True
    assert eigenspec["effective_rank"] <= 20

    q, b = LowRankEngine.randomized_svd(low_rank_mat, rank=16)
    reconstructed = q @ b
    rel_diff = np.linalg.norm(low_rank_mat - reconstructed) / np.linalg.norm(low_rank_mat)
    assert rel_diff < 1e-4


def test_representations_and_precision():
    contract = ExecutionContract(contract_class=ContractClass.NUMERICALLY_BOUNDED, relative_error=0.05)
    prec = PrecisionEngine.select_precision(contract, sensitivity=0.2)
    assert prec == DataType.INT8

    mat = np.array([-2.5, 0.1, 3.2, -0.05, 1.8], dtype=np.float32)
    ternary, gamma = PrecisionEngine.quantize_to_ternary(mat)
    assert set(np.unique(ternary)).issubset({-1, 0, 1})
    assert gamma > 0.0


def test_memory_engine_aos_soa():
    pts = np.array([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]], dtype=np.float32)
    soa = MemoryEngine.aos_to_soa(pts)
    assert "x" in soa and "y" in soa and "z" in soa
    aos = MemoryEngine.soa_to_aos(soa)
    assert np.allclose(pts, aos)

    pool = MemoryEngine(pool_size_mb=1)
    buf = pool.allocate_buffer(1024)
    assert len(buf) == 1024


def test_heterogeneous_fabric_partition():
    part_small = HeterogeneousFabric.recommend_partition(64, 64, 64, arithmetic_intensity=1.0)
    assert part_small["cpu_ratio"] == 1.0

    part_large = HeterogeneousFabric.recommend_partition(4096, 4096, 4096, arithmetic_intensity=20.0)
    assert part_large["igpu_ratio"] >= 0.5


def test_error_budget_tracker():
    tracker = ErrorBudgetTracker(total_budget=0.02)
    assert tracker.allocate_stage("Stage1", 0.005) is True
    assert tracker.allocate_stage("Stage2", 0.010) is True
    assert tracker.remaining_budget == pytest.approx(0.005)
    assert tracker.allocate_stage("Stage3", 0.010) is False  # Exceeds total 0.02
    assert tracker.is_valid is False
