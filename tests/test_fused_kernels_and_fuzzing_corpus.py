"""
tests/test_fused_kernels_and_fuzzing_corpus.py
===============================================
Automated validation for:
1. OpenVINO Subgraph Fused Kernels & Zero-Sync Pipeline (hyper_universal/backends/openvino_ir_exporter.py)
2. Continuous Adversarial Counterexample Fuzzing Corpus Persistence (hyper_universal/counterexamples/engine.py)
3. Pipeline Stage 15 automatic counterexample recording into the fuzzing corpus.
"""

import os
import tempfile
import numpy as np
import pytest

from hyper_universal.backends.openvino_ir_exporter import OpenVINOSubgraphExporter
from hyper_universal.counterexamples.engine import CounterexampleEngine, Counterexample
from hyper_universal.pipeline import UnifiedComputationalEscapePipeline


def test_openvino_fused_subgraph_execution():
    """Verify that fused GEMM+Bias+ReLU executes correctly and eliminates host sync."""
    exporter = OpenVINOSubgraphExporter()
    
    np.random.seed(42)
    A = np.random.randn(16, 32).astype(np.float32)
    B = np.random.randn(32, 24).astype(np.float32)
    bias = np.random.randn(24).astype(np.float32)

    res = exporter.execute_fused_gemm_bias_relu(A, B, bias, prefer_gpu=True)

    # Reference check
    ref = np.maximum(np.dot(A, B) + bias, 0.0)
    assert np.allclose(res.output, ref, atol=1e-4)
    assert res.is_fused is True
    assert res.host_sync_eliminated is True
    assert res.latency_ms >= 0.0
    assert res.actual_device in ["GPU", "CPU", "CPU_FALLBACK"]


def test_persistent_counterexample_fuzzing_corpus():
    """Verify that failed counterexamples are persistently written to and read from disk."""
    with tempfile.TemporaryDirectory() as tmpdir:
        corpus_file = os.path.join(tmpdir, "test_fuzzing_corpus.json")
        engine1 = CounterexampleEngine(corpus_path=corpus_file)

        # Record external counterexample
        cx = engine1.record_external_counterexample(
            workload_id="gemm_boundary_overflow",
            candidate_id="xf_sparse_dense_misprediction",
            error_desc="Adversarial Cauchy noise caused 14.5% output divergence",
            divergence=0.145,
        )

        assert os.path.exists(corpus_file)
        assert len(engine1.counterexample_db) == 1

        # Second engine instance must load the persisted corpus
        engine2 = CounterexampleEngine(corpus_path=corpus_file)
        assert len(engine2.counterexample_db) == 1
        loaded_cx = engine2.counterexample_db[0]
        assert loaded_cx.workload_id == "gemm_boundary_overflow"
        assert loaded_cx.candidate_id == "xf_sparse_dense_misprediction"
        assert loaded_cx.divergence == 0.145


def test_pipeline_stage15_records_into_fuzzing_corpus():
    """Verify that pipeline Stage 15 logs divergence into the counterexample engine."""
    pipeline = UnifiedComputationalEscapePipeline()
    mat = np.ones((8, 8), dtype=np.float32)

    initial_corpus_count = len(pipeline.counterexample_engine.counterexample_db)

    # Execute with diverging kernel
    ctx = pipeline.execute(
        workload_id="test_corpus_integration",
        input_data=mat,
        execute_fn=lambda x: x + 50.0,
        reference_oracle_fn=lambda x: x * 1.0,
    )

    assert ctx.counterexample_detected is True
    assert len(pipeline.counterexample_engine.counterexample_db) == initial_corpus_count + 1
    newest_cx = pipeline.counterexample_engine.counterexample_db[-1]
    assert newest_cx.workload_id == "test_corpus_integration"
