"""
LEO V45 Breakthroughs Unit and Integration Tests
Verifies LNS arithmetic, CAT cache pinning, Fourier sparsification, VSA crystallization, and zero-copy streaming.
"""
import pytest
import torch
import numpy as np
from core.quantum.breakthrough.lns_compiler import LNSCompiler
from core.quantum.breakthrough.intel_cat import IntelCATManager
from core.quantum.breakthrough.fourier_attention import FourierAttentionPruner
from core.quantum.breakthrough.vsa_crystallizer_v2 import VSACrystallizerV2
from core.quantum.breakthrough.oneapi_zerocopy import OneAPIZeroCopy
from core.quantum.breakthrough.recursive_crystallizer import RecursiveCrystallizer


def test_lns_compiler():
    compiler = LNSCompiler(base=2.0)
    
    # Test tensor mapping
    A = torch.tensor([[2.0, 0.0], [-4.0, 8.0]])
    signs, logs = compiler.to_lns(A)
    
    assert torch.equal(signs, torch.tensor([[1.0, 0.0], [-1.0, 1.0]]))
    # log2(2) = 1, log2(4) = 2, log2(8) = 3
    assert logs[0, 0].item() == 1.0
    assert logs[1, 0].item() == 2.0
    assert logs[1, 1].item() == 3.0
    
    # Reconstruction check
    A_reconstructed = compiler.from_lns(signs, logs)
    assert torch.allclose(A, A_reconstructed)
    
    # Multiplication checks
    sa, la = compiler.to_lns(torch.tensor([2.0]))
    sb, lb = compiler.to_lns(torch.tensor([8.0]))
    s_prod, l_prod = compiler.multiply_lns(sa, la, sb, lb)
    prod = compiler.from_lns(s_prod, l_prod)
    assert prod.item() == 16.0

    # Matrix multiplication checks
    X = torch.tensor([[1.0, 2.0], [3.0, 4.0]])
    Y = torch.tensor([[5.0, 6.0], [7.0, 8.0]])
    res_lns = compiler.lns_matmul(X, Y)
    res_float = torch.matmul(X, Y)
    assert torch.allclose(res_lns, res_float, atol=1e-4)


def test_intel_cat_manager():
    cat = IntelCATManager(target_cache_fraction=0.5)
    
    # Create mock layers
    class MockLayer(torch.nn.Module):
        def __init__(self):
            super().__init__()
            self.w = torch.nn.Parameter(torch.randn(10, 10))
            
    layers = [MockLayer() for _ in range(4)]
    
    # Pin layers
    pinned = cat.pin_hot_layers(layers)
    assert pinned > 0
    assert len(cat.pinned_buffers) > 0
    
    # Release memory locks
    cat.release_all()
    assert len(cat.pinned_buffers) == 0


def test_fourier_attention():
    pruner = FourierAttentionPruner(keep_ratio=0.1)
    
    # Inputs: [batch, heads, seq_len, head_dim]
    q = torch.randn(2, 4, 16, 32)
    k = torch.randn(2, 4, 16, 32)
    v = torch.randn(2, 4, 16, 32)
    
    out = pruner(q, k, v)
    assert out.shape == (2, 4, 16, 32)


def test_vsa_crystallizer_v2():
    vsa = VSACrystallizerV2(dim=1000, threshold=0.65)
    
    # Verify vector dimension
    hv = vsa.generate_hypervector()
    assert hv.shape == (1000,)
    assert torch.all((hv == 0.0) | (hv == 1.0))
    
    # Verify binding and bundling operations
    hv_a = vsa.generate_hypervector()
    hv_b = vsa.generate_hypervector()
    hv_bound = vsa.bind(hv_a, hv_b)
    assert hv_bound.shape == (1000,)
    
    hv_bundled = vsa.bundle([hv_a, hv_b])
    assert hv_bundled.shape == (1000,)
    
    # Index query mapping
    query = "bypass memory wall"
    response = "use 10000-d VSA"
    vsa.crystallize_query(query, response)
    
    # Query check
    match, sim = vsa.query_crystallized("bypass memory wall")
    assert match == response
    assert sim == 1.0


def test_oneapi_zerocopy():
    zc = OneAPIZeroCopy()
    tensor = torch.randn(5, 5)
    
    shared_tensor = zc.allocate_shared_weight("test_weight", tensor)
    assert shared_tensor.shape == (5, 5)
    assert "test_weight" in zc.active_allocations
    
    streamed = zc.stream_layer_weight("test_weight", tensor)
    assert streamed.shape == (5, 5)


def test_recursive_crystallizer():
    vsa = VSACrystallizerV2(dim=1000, threshold=0.70)
    crystallizer = RecursiveCrystallizer(vsa, auto_crystallize_threshold=2)
    
    query = "optimize thread affinity"
    response = "pin cores 0-3"
    
    # Try 1: Frequency = 1 (should not crystallize)
    res1 = crystallizer.record_and_evaluate(query, response)
    assert res1 is False
    assert len(crystallizer.crystallized_queries) == 0
    
    # Try 2: Frequency = 2 (exceeds/reaches threshold, should crystallize)
    res2 = crystallizer.record_and_evaluate(query, response)
    assert res2 is True
    assert "optimize thread affinity" in crystallizer.crystallized_queries
    
    # Verify mapping registered in VSA space
    vsa_match, sim = vsa.query_crystallized("optimize thread affinity")
    assert vsa_match == response
    assert sim == 1.0
