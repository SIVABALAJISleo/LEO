"""
tests/hyper_escape/test_streaming.py
Validates Out-of-Core Streaming & Memory Escape Execution (Feature B / Section 4.1).
Tests chunked binary file reduction, bounded-memory chunked GEMV,
and layer-by-layer sequential model pipeline.
"""
import os
import tempfile
import pytest
import numpy as np

from hyper_universal.memory_escape.engine import MemoryBudgetController, OutOfCoreStreamEngine


def test_streaming_binary_file_reduction():
    controller = MemoryBudgetController(budget_mb=1024.0, safety_margin_mb=256.0)
    engine = OutOfCoreStreamEngine(controller)

    # Create temporary binary file with 500,000 float32 values (2 MB)
    data = np.arange(500_000, dtype=np.float32)
    expected_sum = float(np.sum(data))

    with tempfile.NamedTemporaryFile(delete=False, suffix=".bin") as f:
        tmp_name = f.name
        f.write(data.tobytes())

    try:
        # Stream in 256 KB chunks (bounded working memory)
        chunk_size = 256 * 1024
        result_sum, report = engine.stream_binary_file_reduction(
            file_path=tmp_name,
            chunk_size_bytes=chunk_size,
            dtype=np.float32,
            reduce_fn=np.sum,
        )

        assert np.isclose(result_sum, expected_sum, rtol=1e-5)
        assert report.total_bytes_streamed == data.nbytes
        assert report.chunk_count == (data.nbytes + chunk_size - 1) // chunk_size
        assert report.peak_memory_used_mb < 50.0  # Kept bounded
    finally:
        if os.path.exists(tmp_name):
            os.remove(tmp_name)


def test_chunked_gemv_exactness():
    controller = MemoryBudgetController(budget_mb=512.0, safety_margin_mb=128.0)
    engine = OutOfCoreStreamEngine(controller)

    # Matrix: 2000 x 500, Vector: 500
    rows, cols = 2000, 500
    np.random.seed(42)
    matrix = np.random.randn(rows, cols).astype(np.float32)
    vector = np.random.randn(cols).astype(np.float32)

    expected_output = matrix @ vector

    # Stream in row blocks of 200 rows
    streamed_output, report = engine.stream_chunked_gemv(matrix, vector, row_chunk_size=200)

    # Check exact numerical match
    assert np.allclose(streamed_output, expected_output, atol=1e-5, rtol=1e-5)
    assert report.chunk_count == 10
    assert report.total_bytes_streamed == matrix.nbytes


def test_layer_by_layer_pipeline():
    controller = MemoryBudgetController(budget_mb=512.0, safety_margin_mb=128.0)
    engine = OutOfCoreStreamEngine(controller)

    # 4 synthetic layers: x -> W1 x -> ReLU -> W2 x -> LayerNorm
    np.random.seed(42)
    x = np.random.randn(128, 64).astype(np.float32)
    w1 = np.random.randn(64, 32).astype(np.float32)
    w2 = np.random.randn(32, 16).astype(np.float32)

    def layer1(inp):
        return inp @ w1

    def layer2(inp):
        return np.maximum(inp, 0.0)

    def layer3(inp):
        return inp @ w2

    layers = [layer1, layer2, layer3]

    # Reference sequential computation
    ref_out = layer3(layer2(layer1(x)))

    # Streamed layer-by-layer execution
    out, report = engine.stream_layer_by_layer_pipeline(x, layers)

    assert np.allclose(out, ref_out, atol=1e-5)
    assert report.chunk_count == 3
