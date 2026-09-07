"""
tests/test_cbe_phase5.py
Unit tests for TemporalSuperResolution, SpatialReconstructor, TinyIntelReconNet,
NeuralReconstructor, and FrameReconstructionPipeline.
"""

import numpy as np
import pytest
import torch

from cbe.reconstruction.spatial_reconstruction import SpatialReconstructor, ContrastAdaptiveSharpener
from cbe.reconstruction.temporal_reconstruction import TemporalSuperResolution
from cbe.reconstruction.neural_reconstruction import TinyIntelReconNet, NeuralReconstructor
from cbe.reconstruction.frame_reconstruction import FrameReconstructionPipeline


def test_contrast_adaptive_sharpening():
    cas = ContrastAdaptiveSharpener(sharpness=0.5)
    img = np.random.uniform(0.2, 0.8, (32, 32, 3)).astype(np.float32)
    sharpened = cas.sharpen(img)
    assert sharpened.shape == (32, 32, 3)
    assert np.all(sharpened >= 0.0) and np.all(sharpened <= 1.0)


def test_spatial_upscaling():
    recon = SpatialReconstructor(sharpness=0.5)
    low_res = np.ones((32, 32, 3), dtype=np.float32) * 0.5
    upscaled = recon.upscale(low_res, target_height=64, target_width=64)
    assert upscaled.shape == (64, 64, 3)


def test_tiny_intel_recon_net_forward():
    net = TinyIntelReconNet(in_channels=8, scale_factor=2)
    # (B=1, C=8, H=32, W=32)
    x = torch.randn(1, 8, 32, 32)
    out = net(x)
    assert out.shape == (1, 3, 64, 64)
    
    # Parameter count verification (<25K params)
    param_count = sum(p.numel() for p in net.parameters())
    assert param_count < 25000


def test_neural_reconstructor_pipeline():
    nr = NeuralReconstructor(enable_ov_gpu=True)
    low_res = np.ones((32, 32, 3), dtype=np.float32) * 0.5
    hist = np.ones((32, 32, 3), dtype=np.float32) * 0.5
    mv = np.zeros((32, 32, 2), dtype=np.float32)
    
    high_res, backend, elapsed = nr.reconstruct(low_res, hist, mv)
    assert high_res.shape == (64, 64, 3)
    assert elapsed > 0.0
    assert "OpenVINO" in backend or "PyTorch" in backend
    
    savings = nr.verify_net_savings(native_render_cost_ms=45.0, low_res_render_cost_ms=10.0)
    assert savings["is_net_beneficial"] is True


def test_frame_reconstruction_pipeline():
    pipeline = FrameReconstructionPipeline(enable_neural=True)
    low_res = np.ones((32, 32, 3), dtype=np.float32) * 0.5
    H, W = 64, 64
    mv = np.zeros((H, W, 2), dtype=np.float32)
    depth = np.ones((H, W), dtype=np.float32) * 5.0
    
    out, telemetry = pipeline.reconstruct_frame(
        low_res_frame=low_res,
        target_height=H,
        target_width=W,
        motion_vectors=mv,
        current_depth=depth,
        prev_depth=depth
    )
    assert out.shape == (H, W, 3)
    assert "method" in telemetry
