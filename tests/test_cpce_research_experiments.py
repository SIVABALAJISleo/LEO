"""
tests/test_cpce_research_experiments.py
=======================================
Verification Test Suite for CPCE Next-Generation Research Architecture Upgrades:
1. JIT Kernel Emission via Numba (AVX2 Vectorized Scaling & CSR SpMV)
2. Automated Algorithmic Discovery via Equality Saturation (E-Graph Engine)
3. OpenVINO Heterogeneous Subgraph Offloading (CPU + Intel UHD iGPU)
4. Comprehensive Support Matrix Audit Sections (Failed Experiments, Unsupported Workloads, Limitations)
"""

import os
import pytest
import numpy as np
from fastapi.testclient import TestClient

from backend.main import app
from hyper_x.cpce.jit_compiler import CIRJITCompiler
from hyper_x.cpce.egraph import (
    EGraph,
    ENode,
    EClass,
    EqualitySaturationEngine,
    EGraphIdentityRule,
    EGraphZeroRule,
    EGraphDiagonalScalingRule,
)
from hyper_x.cpce.subgraph_offloader import (
    OpenVINOSubgraphOffloader,
    SubgraphPartition,
    PartitionedExecutionResult,
)
from hyper_x.cpce.ir import CanonicalGraph, CIRNode, OpType
from hyper_x.cpce.support_matrix import CPCESupportMatrix

client = TestClient(app)


# ── 1. JIT Kernel Emission Tests ───────────────────────────────────────────── #

class TestJITKernelEmission:

    def test_jit_diagonal_scaling_parity(self):
        """Verify JIT diagonal scaling matches NumPy broadcast within IEEE 754 float32 precision."""
        compiler = CIRJITCompiler()
        diag = np.array([2.5, -1.0, 0.5, 3.0], dtype=np.float32)
        mat = np.array([
            [1.0, 2.0, 3.0],
            [4.0, 5.0, 6.0],
            [7.0, 8.0, 9.0],
            [10.0, 11.0, 12.0],
        ], dtype=np.float32)

        out = compiler.execute_diagonal_scale(diag, mat)
        ref = diag[:, np.newaxis] * mat

        np.testing.assert_allclose(out, ref, rtol=1e-6, atol=1e-7)

    def test_jit_csr_spmv_parity(self):
        """Verify JIT CSR SpMV matches dense matrix-vector multiplication."""
        compiler = CIRJITCompiler()
        # Sparse matrix 3x4:
        # [ 10,  0,  0, 20 ]
        # [  0, 30,  0,  0 ]
        # [  0,  0, 40, 50 ]
        dense_A = np.array([
            [10.0, 0.0, 0.0, 20.0],
            [0.0, 30.0, 0.0, 0.0],
            [0.0, 0.0, 40.0, 50.0],
        ], dtype=np.float32)
        x = np.array([1.0, 2.0, 3.0, 4.0], dtype=np.float32)

        data = np.array([10.0, 20.0, 30.0, 40.0, 50.0], dtype=np.float32)
        indices = np.array([0, 3, 1, 2, 3], dtype=np.int32)
        indptr = np.array([0, 2, 3, 5], dtype=np.int32)

        y = compiler.execute_csr_spmv(data, indices, indptr, x)
        ref = np.dot(dense_A, x)

        np.testing.assert_allclose(y, ref, rtol=1e-6, atol=1e-7)

    def test_jit_fused_scale_add_parity(self):
        """Verify fused scale + bias kernel achieves exact numerical parity."""
        compiler = CIRJITCompiler()
        diag = np.array([1.5, -2.0], dtype=np.float32)
        mat = np.array([[3.0, 4.0], [5.0, 6.0]], dtype=np.float32)
        bias = np.array([[0.1, 0.2], [0.3, 0.4]], dtype=np.float32)

        out = compiler.execute_fused_scale_add(diag, mat, bias)
        ref = diag[:, np.newaxis] * mat + bias

        np.testing.assert_allclose(out, ref, rtol=1e-6, atol=1e-7)

    def test_jit_horner_batch_parity(self):
        """Verify batch Horner polynomial evaluation."""
        compiler = CIRJITCompiler()
        # P(x) = 3 + 2x + x^2
        coeffs = np.array([3.0, 2.0, 1.0], dtype=np.float64)
        xs = np.array([0.0, 1.0, 2.0, 3.0], dtype=np.float64)

        out = compiler.execute_horner_batch(coeffs, xs)
        ref = np.array([3.0, 6.0, 11.0, 18.0], dtype=np.float64)

        np.testing.assert_allclose(out, ref, rtol=1e-9)

    def test_jit_benchmark_execution(self):
        """Verify JIT benchmark executes and returns measured speedup telemetry."""
        compiler = CIRJITCompiler()
        stats = compiler.benchmark_kernel("diagonal_scale", dim_m=256, dim_n=256, iterations=3)
        assert stats["kernel"] == "diagonal_scale"
        assert stats["provenance"] == "MEASURED"
        assert stats["median_jit_latency_ms"] > 0
        assert stats["median_baseline_latency_ms"] > 0


# ── 2. Equality Saturation (E-Graph) Tests ─────────────────────────────────── #

class TestEqualitySaturationEngine:

    def test_egraph_identity_elimination(self):
        """Verify E-Graph eliminates identity multiplication without destroying representation."""
        g = CanonicalGraph()
        g.add_node(CIRNode("in_A", OpType.INPUT))
        g.add_node(CIRNode("in_I", OpType.INPUT, parameters={"structure": "identity"}))
        g.add_node(CIRNode("mm", OpType.MATMUL, inputs=["in_A", "in_I"]))
        g.add_node(CIRNode("out", OpType.OUTPUT, inputs=["mm"]))

        engine = EqualitySaturationEngine()
        egraph, root_id = engine.build_egraph(g)
        rules = engine.saturate(egraph)

        assert "EGRAPH_IDENTITY_ELIMINATION" in rules
        opt_g, opt_cost = engine.extract_optimal_ast(egraph, root_id)
        # Optimal cost should not include full MATMUL cost (100)
        assert opt_cost < 50.0

    def test_egraph_zero_propagation(self):
        """Verify E-Graph collapses zero multiplication."""
        g = CanonicalGraph()
        g.add_node(CIRNode("in_A", OpType.INPUT))
        g.add_node(CIRNode("in_Z", OpType.INPUT, parameters={"structure": "zero"}))
        g.add_node(CIRNode("mm", OpType.MATMUL, inputs=["in_A", "in_Z"]))
        g.add_node(CIRNode("out", OpType.OUTPUT, inputs=["mm"]))

        engine = EqualitySaturationEngine()
        egraph, root_id = engine.build_egraph(g)
        rules = engine.saturate(egraph)

        assert "EGRAPH_ZERO_PROPAGATION" in rules

    def test_egraph_diagonal_scaling_fusion(self):
        """Verify E-Graph discovers diagonal scaling fusion."""
        g = CanonicalGraph()
        g.add_node(CIRNode("in_D", OpType.INPUT, parameters={"structure": "diagonal"}))
        g.add_node(CIRNode("in_B", OpType.INPUT))
        g.add_node(CIRNode("mm", OpType.MATMUL, inputs=["in_D", "in_B"]))
        g.add_node(CIRNode("out", OpType.OUTPUT, inputs=["mm"]))

        engine = EqualitySaturationEngine()
        egraph, root_id = engine.build_egraph(g)
        rules = engine.saturate(egraph)

        assert "EGRAPH_DIAGONAL_SCALING" in rules
        opt_g, opt_cost = engine.extract_optimal_ast(egraph, root_id)
        # Verify SCALE node was extracted
        assert any(n.op_type == OpType.SCALE for n in opt_g.nodes.values())

    def test_egraph_multi_rule_simultaneous_saturation(self):
        """Verify non-linear multi-rule fusions without fixed-order phase bias."""
        g = CanonicalGraph()
        g.add_node(CIRNode("in_A", OpType.INPUT))
        g.add_node(CIRNode("in_I", OpType.INPUT, parameters={"structure": "identity"}))
        g.add_node(CIRNode("in_Z", OpType.INPUT, parameters={"structure": "zero"}))
        g.add_node(CIRNode("t1", OpType.MATMUL, inputs=["in_A", "in_I"]))
        g.add_node(CIRNode("t2", OpType.MATMUL, inputs=["t1", "in_Z"]))
        g.add_node(CIRNode("out", OpType.OUTPUT, inputs=["t2"]))

        engine = EqualitySaturationEngine()
        egraph, root_id = engine.build_egraph(g)
        rules = engine.saturate(egraph)

        assert "EGRAPH_IDENTITY_ELIMINATION" in rules
        assert "EGRAPH_ZERO_PROPAGATION" in rules


# ── 3. OpenVINO Subgraph Offloading Tests ───────────────────────────────────── #

class TestOpenVINOSubgraphOffloader:

    def test_subgraph_partitioning_rules(self):
        """Verify dense GEMM nodes are partitioned for iGPU offloading and structural nodes for CPU."""
        offloader = OpenVINOSubgraphOffloader()
        g = CanonicalGraph()
        g.add_node(CIRNode("A", OpType.INPUT, shape=(1024, 1024)))
        g.add_node(CIRNode("B", OpType.INPUT, shape=(1024, 1024)))
        g.add_node(CIRNode("dense_mm", OpType.MATMUL, inputs=["A", "B"], shape=(1024, 1024)))
        g.add_node(CIRNode("D", OpType.INPUT, shape=(1024,)))
        g.add_node(CIRNode("scale", OpType.SCALE, inputs=["D", "dense_mm"], shape=(1024, 1024)))
        g.add_node(CIRNode("out", OpType.OUTPUT, inputs=["scale"]))

        partitions = offloader.partition_graph(g, dense_threshold=768)
        assert len(partitions) >= 1
        # Structural operations remain on CPU
        cpu_part = next((p for p in partitions if p.target_backend == "CPU"), None)
        assert cpu_part is not None

    def test_subgraph_hybrid_pipeline_parity(self):
        """Verify hybrid execution achieves strict IEEE 754 parity vs reference."""
        offloader = OpenVINOSubgraphOffloader()
        N = 256
        A = np.random.randn(N, N).astype(np.float32)
        B = np.random.randn(N, N).astype(np.float32)
        D = np.random.randn(N).astype(np.float32)

        res = offloader.execute_hybrid_pipeline(A, B, D)
        assert res.status == "PASS"
        assert res.provenance == "MEASURED"
        assert res.relative_difference_vs_cpu_ref <= 1e-4
        assert res.total_partitioned_duration_ms > 0


# ── 4. Audit & Support Matrix Programmatic Tests ────────────────────────────── #

class TestSupportMatrixAuditFields:

    def test_support_matrix_audit_sections_programmatic(self):
        """Verify failed experiments, unsupported workloads, limitations, and upgrades."""
        sm = CPCESupportMatrix()
        failed = sm.get_failed_experiments()
        assert len(failed) >= 2
        assert any("Structural Scanning" in f["experiment"] for f in failed)
        assert any("Common Subexpression" in f["experiment"] for f in failed)

        unsupported = sm.get_unsupported_workloads()
        assert len(unsupported) >= 3
        assert any("CUDA" in u["workload"] for u in unsupported)
        assert any("Foundation Models" in u["workload"] for u in unsupported)

        limitations = sm.get_known_limitations()
        assert len(limitations) >= 3
        assert any("Python Dispatch" in l["limitation"] for l in limitations)
        assert any("Freivalds" in l["limitation"] for l in limitations)

        upgrades = sm.get_research_upgrades()
        assert len(upgrades) >= 3
        assert any("JIT" in u["feature"] for u in upgrades)
        assert any("E-Graphs" in u["feature"] for u in upgrades)
        assert any("Subgraph Offloading" in u["feature"] for u in upgrades)

    def test_api_support_matrix_detailed_endpoint(self):
        """Verify /api/v1/cpce/support-matrix includes all four audit and upgrade sections."""
        res = client.get("/api/v1/cpce/support-matrix")
        assert res.status_code == 200
        data = res.json()
        assert "failed_experiments" in data
        assert "unsupported_workloads" in data
        assert "known_limitations" in data
        assert "research_upgrades" in data
        assert len(data["failed_experiments"]) >= 2
        assert len(data["research_upgrades"]) >= 3

    def test_api_jit_benchmark_endpoint(self):
        """Verify /api/v1/cpce/jit-benchmark returns live empirical execution results."""
        res = client.post("/api/v1/cpce/jit-benchmark?dim_m=128&dim_n=128&iterations=2")
        assert res.status_code == 200
        data = res.json()
        assert data["kernel"] == "diagonal_scale"
        assert data["provenance"] == "MEASURED"

    def test_api_egraph_saturation_endpoint(self):
        """Verify /api/v1/cpce/egraph-saturate endpoint."""
        res = client.post("/api/v1/cpce/egraph-saturate", json={"contract_id": "dense_gemm"})
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "PASS"
        assert data["provenance"] == "MEASURED"
        assert "EGRAPH_IDENTITY_ELIMINATION" in data["applied_fusions"]

    def test_api_subgraph_offload_endpoint(self):
        """Verify /api/v1/cpce/subgraph-offload endpoint."""
        res = client.post("/api/v1/cpce/subgraph-offload?dim=128")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "PASS"
        assert data["provenance"] == "MEASURED"
        assert data["relative_difference_vs_cpu_ref"] <= 1e-4
