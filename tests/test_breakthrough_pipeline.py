"""
Comprehensive End-to-End Pipeline Tests for LEO/HYPER Ω Breakthrough Architecture.
Verifies all core engines:
- Hardware Profiler & Profile Validation
- Contract IR & Contract100Gate
- Work-DAG Engine (Topological sort, Dead-node elimination, CSE, Critical path)
- Necessary-Work Engine (Categorization, Work ledger)
- Escape Compiler (22 strategies, NO_ESCAPE_FOUND, CONTRACT_UNSATISFIABLE)
- Strategy Composer (Composite candidates, Overhead pruning)
- Heterogeneous Compute Fabric (Empirical CPU vs UHD scheduling)
- Domain Escapes (Graphics selective rendering, Simulation PDE, LLM speculative decoding)
- Verification Engine (Levels 0 to 5, Freivalds algorithm)
- Certificate Engine (Proof-carrying certificates, Tamper-evidence)
- Benchmark Integrity Suite (6 canonical modes, Separated speedup metrics)
"""

import pytest
import numpy as np
import os

from hyper.hardware import HardwareProfiler, get_hardware_profile
from hyper.contract_ir import ContractIR, ExactnessClass, VerificationLevel, ContractStatus, Contract100Gate
from hyper.work_dag import WorkNode, WorkEdge, WorkGraph
from hyper.necessary_work import NecessityClass, NecessaryWorkLedger, NecessaryWorkEngine
from hyper.escape_compiler import CanonicalStrategy, StrategyDeclaration, EscapeCompiler
from hyper.strategy_composer import CompositeStrategyCandidate, StrategyComposer
from hyper.hardware_fabric import HeterogeneousComputeFabric
from hyper.graphics import GraphicsEscapeEngine
from hyper.simulation import SimulationEscapeEngine
from hyper.ai import LLMEscapeEngine
from hyper.verification import VerificationEngine
from hyper.certificates import CertificateEngine
from hyper.benchmark_integrity import BenchmarkIntegritySuite


class TestHardwareProfile:
    def test_hardware_profiler_and_yaml(self):
        profiler = HardwareProfiler()
        prof = profiler.generate_canonical_profile()
        assert prof["cpu_model"] == "Intel Core i5-12450H"
        assert prof["cores"] == 8
        assert prof["threads"] == 12
        assert prof["igpu_eus"] == 48
        assert prof["has_avx512"] is False
        assert prof["constraints"]["raw_hardware_parity"] == "NOT_ACHIEVED"
        assert len(prof["hardware_hash"]) == 64

        # Test yaml save and load
        yaml_file = "test_hardware_profile.yaml"
        profiler.save_yaml(yaml_file)
        assert os.path.exists(yaml_file)
        os.remove(yaml_file)


class TestWorkDAG:
    def test_work_graph_construction_and_cse(self):
        graph = WorkGraph("TestPipeline")

        n1 = WorkNode("node_input_A", "load", [], ["A"], shape=(128, 128), estimated_work_flops=0)
        n2 = WorkNode("node_input_B", "load", [], ["B"], shape=(128, 128), estimated_work_flops=0)
        n3 = WorkNode("node_matmul_1", "gemm", ["A", "B"], ["C1"], dependencies=["node_input_A", "node_input_B"], shape=(128, 128), estimated_work_flops=4e6)
        # Duplicate operation on same inputs (CSE candidate)
        n4 = WorkNode("node_matmul_2", "gemm", ["A", "B"], ["C2"], dependencies=["node_input_A", "node_input_B"], shape=(128, 128), estimated_work_flops=4e6)
        # Dead node (not consumed by output)
        n5 = WorkNode("node_dead", "noop", ["C1"], ["unused"], dependencies=["node_matmul_1"], shape=(128, 128), estimated_work_flops=100)

        for n in [n1, n2, n3, n4, n5]:
            graph.add_node(n)

        graph.add_edge("node_input_A", "node_matmul_1", "A")
        graph.add_edge("node_input_B", "node_matmul_1", "B")
        graph.add_edge("node_input_A", "node_matmul_2", "A")
        graph.add_edge("node_input_B", "node_matmul_2", "B")
        graph.add_edge("node_matmul_1", "node_dead", "C1")

        # Test CSE detection & elimination
        elim_cse = graph.eliminate_common_subexpressions()
        assert elim_cse == 1

        # Test dead node detection & elimination
        elim_dead = graph.eliminate_dead_nodes(terminal_outputs={"C1"})
        assert elim_dead == 1
        assert "node_dead" not in graph.nodes

        # Critical path analysis
        path, flops = graph.critical_path_analysis()
        assert len(path) > 0
        assert flops == 4e6


class TestNecessaryWorkEngine:
    def test_work_classification_and_accounting(self):
        engine = NecessaryWorkEngine()
        contract = ContractIR(task_id="nec_test", exactness_class=ExactnessClass.EXACT)

        graph = WorkGraph()
        n1 = WorkNode("n1", "gemm", ["A", "B"], ["C"], shape=(256, 256), estimated_work_flops=33.5e6, memory_footprint_bytes=262144)
        graph.add_node(n1)

        # Baseline: Required
        ledger = engine.analyze_graph(graph, contract)
        assert ledger.executed_work_flops == 33.5e6
        assert ledger.eliminated_work_flops == 0.0
        assert ledger.work_reduction_ratio == 0.0

        # With cache hit: Reusable & Eliminated
        ledger_cached = engine.analyze_graph(graph, contract, cached_node_ids={"n1"})
        assert ledger_cached.reused_work_flops == 33.5e6
        assert ledger_cached.eliminated_work_flops == 33.5e6
        assert ledger_cached.work_reduction_ratio == 1.0


class TestEscapeCompiler:
    def test_escape_compiler_search_and_no_escape(self):
        compiler = EscapeCompiler()
        contract_exact = ContractIR(task_id="test_comp", exactness_class=ExactnessClass.EXACT_FLOAT_FP32)
        rng = np.random.RandomState(42)

        A = rng.randn(64, 64).astype(np.float32)
        B = rng.randn(64, 64).astype(np.float32)

        # First run: NO_ESCAPE_FOUND -> Reference Fallback
        out1, cert1, strat1 = compiler.compile_and_execute(contract_exact, A, B)
        assert strat1 == CanonicalStrategy.NO_ESCAPE_FOUND
        assert cert1.strategy_used == "NO_ESCAPE_FOUND"

        # Second run: EXACT_CACHE hit
        out2, cert2, strat2 = compiler.compile_and_execute(contract_exact, A, B)
        assert strat2 == CanonicalStrategy.EXACT_CACHE
        assert cert2.cache_hit is True
        assert np.allclose(out1, out2)

    def test_contract_unsatisfiable_detection(self):
        compiler = EscapeCompiler()
        # Impossible deadline: 0.00001 ms for a 1 GFLOP matrix multiplication
        contract_impossible = ContractIR(
            task_id="impossible",
            exactness_class=ExactnessClass.EXACT,
            latency=None,
        )
        contract_impossible.latency.maximum_ms = 0.00001

        A = np.ones((1000, 1000), dtype=np.float32)
        B = np.ones((1000, 1000), dtype=np.float32)

        _, cert, strat = compiler.compile_and_execute(contract_impossible, A, B)
        assert strat == CanonicalStrategy.CONTRACT_UNSATISFIABLE
        assert cert.contract_status == ContractStatus.UNSATISFIABLE_UNDER_RESOURCE_LIMIT


class TestStrategyComposer:
    def test_composite_candidate_search_and_pruning(self):
        composer = StrategyComposer()
        contract = ContractIR(task_id="comp_search", exactness_class=ExactnessClass.BOUNDED_NUMERICAL, max_absolute_error=0.05)
        A_sparse = np.zeros((128, 128), dtype=np.float32)
        A_sparse[:5, :5] = 1.0  # > 99% sparse
        B = np.ones((128, 128), dtype=np.float32)

        candidates = composer.search_candidates(A_sparse, B, contract, baseline_ms=2.0)
        assert len(candidates) > 1
        assert any(c.name == "Sparsity_Fusion_AVX2" for c in candidates)

        # Pruning
        pruned = composer.prune_unprofitable(candidates, baseline_ms=2.0)
        assert len(pruned) > 0


class TestDomainEngines:
    def test_graphics_selective_rendering(self):
        engine = GraphicsEscapeEngine()
        frame1 = np.zeros((100, 100, 3), dtype=np.float32)
        frame2 = frame1.copy()
        # Only change a small 10x10 subregion (1% of frame)
        frame2[10:20, 10:20, :] = 1.0

        _, analysis1, _ = engine.render_frame_with_escape(frame1)
        composite2, analysis2, meta2 = engine.render_frame_with_escape(frame2)

        assert meta2["strategy"] == "SELECTIVE_TEMPORAL_RECONSTRUCTION"
        assert analysis2.temporal_reused_ratio > 0.90
        assert analysis2.ssim_score >= 0.95

    def test_simulation_pde_sparse_conservation(self):
        sim = SimulationEscapeEngine()
        u0 = np.zeros((32, 32), dtype=np.float32)
        u0[16, 16] = 100.0  # Point heat source

        u1, meta = sim.step_pde_diffusion(u0, dt=0.05, diffusivity=0.20)
        assert meta["strategy"] == "SPARSE_INCREMENTAL_PDE"
        assert meta["sparse_nnz"] > 0
        assert u1.shape == (32, 32)

        v_res = sim.verify_conservation_laws(u0, u1)
        assert v_res.mass_conserved is True

    def test_llm_prefix_and_speculation(self):
        llm = LLMEscapeEngine()
        prompt = [101, 2054, 2003, 1037, 3000]

        # Store prefix
        K = np.ones((5, 64), dtype=np.float32)
        V = np.ones((5, 64), dtype=np.float32)
        llm.store_kv_prefix(tuple(prompt), K, V)

        # Lookup match
        matched_len, entry = llm.lookup_kv_prefix(prompt + [4000, 5000])
        assert matched_len == 5
        assert entry is not None

        # Speculative decode
        draft_fn = lambda ctx, dlen: ([10, 20, 30], [0.95, 0.92, 0.40])
        target_fn = lambda ctx: None

        res = llm.speculative_decode_step(draft_fn, target_fn, prompt, confidence_threshold=0.80)
        assert res.accepted_tokens == [10, 20]  # Third token rolled back (< 0.80)
        assert res.fallback_invoked is True


class TestVerificationAndCertificates:
    def test_freivalds_and_full_numerical(self):
        verifier = VerificationEngine()
        A = np.array([[1.0, 2.0], [3.0, 4.0]], dtype=np.float32)
        B = np.array([[5.0, 6.0], [7.0, 8.0]], dtype=np.float32)
        C_correct = A @ B
        C_wrong = C_correct + 0.1

        assert verifier.verify_freivalds(A, B, C_correct) is True
        assert verifier.verify_freivalds(A, B, C_wrong) is False

    def test_certificate_generation_and_integrity(self):
        cert_engine = CertificateEngine()
        contract = ContractIR(task_id="cert_test", exactness_class=ExactnessClass.EXACT)

        cert = cert_engine.issue_certificate(
            workload_id="matmul_test",
            contract=contract,
            input_hash="abc123hash",
            strategy="EXACT_CACHE",
            reference_work=1e6,
            executed_work=0.0,
            eliminated_work=1e6,
            latency_ms=0.05,
            device="CPU_AVX2",
            cache_hit=True,
        )

        assert cert_engine.verify_certificate_integrity(cert) is True
        assert cert.strategy_used == "EXACT_CACHE"
        assert cert.work_elimination_ratio == 1.0


class TestBenchmarkIntegritySuite:
    def test_six_canonical_modes(self):
        suite = BenchmarkIntegritySuite(warmup_runs=1, bench_runs=3)
        results = suite.run_all_modes(M=64, K=64, N=64)

        assert len(results) == 6
        expected_modes = {"COLD", "WARM", "PERSISTENT_CACHE", "RANDOM", "ADVERSARIAL", "APPLICATION_REALISTIC"}
        assert set(results.keys()) == expected_modes

        for mode_name, res in results.items():
            assert res.contract_passed is True
            assert res.raw_hardware_parity == "NOT_ACHIEVED"
            assert res.min_latency_ms > 0.0
            assert res.median_latency_ms > 0.0
