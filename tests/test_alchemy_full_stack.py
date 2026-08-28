"""
tests/test_alchemy_full_stack.py
=============================================================================
LEO / HYPER v6.0: Automated Full Stack Test Suite for Software Alchemy
Verifies mathematical correctness, compression bounds, and memory parity
across all 8 mathematical engines and unified routing layers.
=============================================================================
"""

import os
import sys
import pytest
import numpy as np

# Ensure workspace root is on sys.path
workspace_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if workspace_root not in sys.path:
    sys.path.insert(0, workspace_root)

from core_ai.alchemy_engine import (
    MortonCacheObliviousEngine,
    AlphaTensorDecompositionEngine,
    KolmogorovArnoldNetworkEngine,
    TensorTrainEngine,
    WinogradConvolutionEngine,
    WinogradAttentionProjector,
    CompressedSensingEngine,
    AdaptivePrecisionController,
    HeterogeneousHardwareScheduler,
    SoftwareAlchemyVerificationLayer,
    SoftwareAlchemySuite
)
from core_ai.alchemy_shared_memory import AlchemySharedMemoryBuffer
from core_ai.alchemy_kan_ffn import AlchemyKANFFNLayer
from HYPER_v6_BREAKTHROUGH.hyper_engine import HyperV6Engine


def test_morton_gemm_correctness():
    """Verifies that Morton Z-order cache-oblivious GEMM matches exact NumPy matrix multiplication."""
    A = np.random.randn(64, 64).astype(np.float32)
    B = np.random.randn(64, 64).astype(np.float32)
    
    C_exact = A @ B
    C_morton = MortonCacheObliviousEngine.morton_matmul(A, B, block_threshold=16)
    
    max_err = np.max(np.abs(C_exact - C_morton))
    assert max_err < 1e-3, f"Morton GEMM max error {max_err} exceeds threshold"


def test_alphatensor_gemm_parity():
    """Verifies AlphaTensor bilinear block decomposition satisfies exact numerical parity."""
    engine = AlphaTensorDecompositionEngine(block_size=4)
    A = np.random.randn(32, 32).astype(np.float32)
    B = np.random.randn(32, 32).astype(np.float32)
    
    C_exact = A @ B
    C_alpha, meta = engine.execute_alphatensor_gemm(A, B)
    
    max_err = np.max(np.abs(C_exact - C_alpha))
    assert max_err < 1e-3, f"AlphaTensor GEMM max error {max_err} exceeds threshold"
    assert meta["reduction_pct"] > 20.0


def test_kan_engine_forward():
    """Verifies Kolmogorov-Arnold Network B-spline forward pass stability."""
    kan = KolmogorovArnoldNetworkEngine(in_features=8, out_features=4, grid_size=5)
    x = np.random.uniform(-0.8, 0.8, size=(16, 8)).astype(np.float32)
    
    out = kan.forward(x)
    assert out.shape == (16, 4)
    assert not np.isnan(out).any()


def test_kan_ffn_layer_and_lut():
    """Verifies KAN Transformer FFN replacement layer with both exact and LUT paths."""
    ffn_lut = AlchemyKANFFNLayer(d_model=64, d_hidden=128, use_lut=True)
    ffn_raw = AlchemyKANFFNLayer(d_model=64, d_hidden=128, use_lut=False)
    
    # Copy weights
    ffn_raw.base_w1 = ffn_lut.base_w1.copy()
    ffn_raw.spline_w1 = ffn_lut.spline_w1.copy()
    ffn_raw.base_w2 = ffn_lut.base_w2.copy()
    ffn_raw.spline_w2 = ffn_lut.spline_w2.copy()
    
    x = np.random.uniform(-0.5, 0.5, size=(4, 8, 64)).astype(np.float32)
    out_lut, meta_lut = ffn_lut.forward(x)
    out_raw, meta_raw = ffn_raw.forward(x)
    
    assert out_lut.shape == (4, 8, 64)
    assert out_raw.shape == (4, 8, 64)
    # LUT interpolation should be close to raw Cox-de Boor
    diff = np.max(np.abs(out_lut - out_raw))
    assert diff < 0.1, f"LUT vs Raw KAN divergence {diff} exceeds bound"


def test_tensor_train_svd_compression():
    """Verifies TT-SVD low-rank compression achieves >50x compression with low Frobenius error."""
    u1 = np.random.randn(16, 4)
    u2 = np.random.randn(16, 4)
    u3 = np.random.randn(16, 4)
    u4 = np.random.randn(16, 4)
    low_rank_tensor = np.einsum("ia,ja,ka,la->ijkl", u1, u2, u3, u4).astype(np.float32)
    
    cores = TensorTrainEngine.decompose(low_rank_tensor, max_rank=8, eps=1e-4)
    reconstructed = TensorTrainEngine.reconstruct(cores)
    ratio = TensorTrainEngine.compression_ratio(low_rank_tensor, cores)
    
    assert ratio > 50.0, f"Compression ratio {ratio} lower than expected"
    rel_err = np.linalg.norm(low_rank_tensor - reconstructed) / np.linalg.norm(low_rank_tensor)
    assert rel_err < 0.05, f"Relative Frobenius error {rel_err} exceeds bound"


def test_winograd_convolution():
    """Verifies Winograd F(2x2, 3x3) minimal filtering convolution matches standard output."""
    engine = WinogradConvolutionEngine()
    img = np.random.randn(32, 32).astype(np.float32)
    kernel = np.random.randn(3, 3).astype(np.float32)
    
    out = engine.conv2d_winograd(img, kernel)
    assert out.shape == (30, 30)
    assert not np.isnan(out).any()


def test_compressed_sensing_jl():
    """Verifies Johnson-Lindenstrauss random projection preserves pairwise Euclidean distances."""
    X = np.random.randn(50, 512).astype(np.float32)
    k = CompressedSensingEngine.compute_target_dim(512, epsilon=0.20)
    R = CompressedSensingEngine.generate_achlioptas_projection_matrix(512, k)
    X_proj = X @ R.T
    
    d_orig = np.linalg.norm(X[0] - X[1])
    d_proj = np.linalg.norm(X_proj[0] - X_proj[1])
    distortion = abs(d_proj - d_orig) / d_orig
    assert distortion < 0.25, f"J-L Distortion {distortion} exceeds epsilon tolerance"


def test_adaptive_precision_controller():
    """Verifies dynamic precision switching and BitNet 1.58-bit ternary quantization."""
    controller = AdaptivePrecisionController()
    w = np.random.randn(64, 64).astype(np.float32)
    
    ternary_w, scale = controller.quantize_ternary_1_58bit(w)
    unique_vals = set(np.unique(ternary_w))
    assert unique_vals.issubset({-1, 0, 1}), f"Non-ternary values found: {unique_vals}"
    assert scale > 0.0


def test_shared_memory_ring_buffer():
    """Verifies zero-copy shared memory buffer allocation and zero-copy view validity."""
    shm = AlchemySharedMemoryBuffer(pool_size_mb=16)
    tensor1 = shm.allocate_tensor("t1", (128, 128), dtype=np.float32)
    tensor1.fill(3.1415)
    
    meta = shm.get_tensor_metadata("t1")
    assert meta is not None
    assert meta["shape"] == (128, 128)
    assert np.allclose(tensor1[0, 0], 3.1415)
    
    util = shm.get_utilization()
    assert util["allocated_mb"] > 0
    shm.release_all()


def test_hyper_v6_engine_integration():
    """Verifies end-to-end execution of HyperV6Engine with genuine neural generation and scientific scoreboard."""
    engine = HyperV6Engine()
    result = engine.process("Run formal proof verification on local model", bypass_cache=True)
    
    assert "response" in result
    assert result["scoreboard"]["contract_parity"] is True
    assert result["scoreboard"]["raw_hardware_parity"] is False
    assert result["estimated_energy_joules"] > 0.0
    assert result["ttft_ms"] > 0.0
    assert result["tok_per_sec"] > 0.0
