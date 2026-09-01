"""
tests/test_audit_rectifications_complete.py
============================================
Comprehensive End-to-End Verification Suite for All HYPER & LEO Breakthrough Modules:
1. Neural GEMM Surrogate (Randomized Sketch Projection)
2. Compressed Sensing FFT (OMP Spectral Reconstruction)
3. Tensor Train GEMM (Low-Rank TT-Core Factorization)
4. Multi-Fidelity Rendering Contract (Stochastic Raytracing & Bilateral Denoising)
5. Causal Physics Simulation (Symplectic Leapfrog Multi-Body Dynamics)
6. AlphaTensor Shape Specialization (49-Mult 4x4 Bilinear Factorization)
7. Oracle Cache (High-Precision FAISS/NumPy Dense Vector Indexing)
8. Prompt Lookup Speculative Decoding (PLD Zero-Weight Extraction & Verification)
9. Heterogeneous Vulkan Local Inference Orchestrator
10. Safe Math AST Evaluator in CacheManager
"""

import os
import sys
import numpy as np
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core_ai.neural_gemm_surrogate import NeuralGEMMSurrogate
from spectral.compressed_sensing_fft import CompressedSensingFFT
from core_ai.tensor_train_gemm import TensorTrainGEMM
from render.rendering_contract import RenderingContract, calculate_ssim, calculate_psnr
from physics.causal_simulation import CausalSimulationModel
from core_ai.alphatensor_specializer import AlphaTensorSpecializer
from core_ai.oracle_cache import OracleCache
from core_ai.prompt_lookup_decoder import PromptLookupDecoder
from backend.inference.pld_integration import PLDIntegratedDecoder
from backend.layer5_local_infer.vulkan_orchestrator import VulkanOrchestrator
from core_ai.cache_manager import safe_math_eval, CacheManager


def test_neural_gemm_surrogate():
    surrogate = NeuralGEMMSurrogate(sketch_rank=16)
    rng = np.random.RandomState(42)
    # Low-rank structured matrix
    U = rng.randn(64, 8).astype(np.float32)
    V = rng.randn(8, 64).astype(np.float32)
    A = U @ V
    B = rng.randn(64, 32).astype(np.float32)
    
    C_pred, latency, rel_error = surrogate.predict(A, B)
    assert C_pred.shape == (64, 32)
    assert latency >= 0.0
    assert rel_error < 0.2  # Bounded approximation error on low-rank matrix


def test_compressed_sensing_fft():
    cs_fft = CompressedSensingFFT(n=512, max_k=8, num_measurements=64)
    t = np.linspace(0, 1, 512, endpoint=False)
    # 2-sparse frequency signal
    signal = np.sin(2 * np.pi * 10 * t) + 0.5 * np.cos(2 * np.pi * 25 * t)
    
    spectrum, latency, method = cs_fft.transform(signal)
    assert len(spectrum) == 512
    assert latency >= 0.0
    assert method == "COMPRESSED_SENSING_OMP"
    assert np.any(np.abs(spectrum) > 0.1)


def test_tensor_train_gemm():
    tt_gemm = TensorTrainGEMM(target_rank=8)
    rng = np.random.RandomState(42)
    A = rng.randn(32, 32).astype(np.float32)
    B = rng.randn(32, 16).astype(np.float32)
    
    C_full, latency, compression_pct = tt_gemm.matmul(A, B)
    assert C_full.shape == (32, 16)
    assert latency >= 0.0
    assert compression_pct > 0.0


def test_rendering_contract():
    renderer = RenderingContract(width=40, height=30)
    
    # Ground truth (32 SPP)
    gt_res = renderer.execute_render(mode=RenderingContract.MODE_GROUND_TRUTH)
    assert gt_res["spp"] == 32
    assert gt_res["ssim"] == 1.0
    assert gt_res["frame"].shape == (30, 40, 3)
    
    # Perceptual (4 SPP + Bilateral Denoise)
    perc_res = renderer.execute_render(mode=RenderingContract.MODE_PERCEPTUAL)
    assert perc_res["spp"] == 4
    assert perc_res["ssim"] >= 0.85
    assert perc_res["psnr"] > 20.0
    assert perc_res["frame"].shape == (30, 40, 3)


def test_causal_physics_simulation():
    sim = CausalSimulationModel(num_particles=16, G=1.0, softening=0.1)
    rng = np.random.RandomState(42)
    pos = rng.randn(16, 3).astype(np.float32)
    vel = rng.randn(16, 3).astype(np.float32) * 0.1
    masses = np.ones(16, dtype=np.float32)
    
    k0, p0, e0 = sim.compute_energy(pos, vel, masses)
    new_pos, new_vel, latency = sim.step_macro(pos, vel, dt=0.01, masses=masses)
    k1, p1, e1 = sim.compute_energy(new_pos, new_vel, masses)
    
    assert new_pos.shape == (16, 3)
    assert new_vel.shape == (16, 3)
    assert latency >= 0.0
    # Energy bounded drift across single symplectic leapfrog step
    assert abs(e1 - e0) / (abs(e0) + 1e-6) < 0.1


def test_alphatensor_specializer():
    specializer = AlphaTensorSpecializer(block_size=4)
    rng = np.random.RandomState(42)
    A = rng.randn(8, 8).astype(np.float32)
    B = rng.randn(8, 8).astype(np.float32)
    
    C_out, latency, meta = specializer.execute_specialized_gemm(A, B)
    C_exact = A @ B
    
    assert C_out.shape == (8, 8)
    assert meta["alphatensor_mults_per_block"] == 49
    assert meta["total_blocks_specialized"] == 8
    # Exact numerical equivalence to standard matmul
    np.testing.assert_allclose(C_out, C_exact, atol=1e-4, rtol=1e-4)


def test_oracle_cache():
    cache = OracleCache(dim=64, default_threshold=0.80)
    cache.add("How do I reset my credentials?", "Navigate to Settings -> Security -> Reset.")
    cache.add("What is the speed of light?", "Approximately 299,792,458 meters per second.")
    
    ans, score, _ = cache.lookup("How do I reset my credentials?")
    assert ans is not None
    assert "Settings" in ans
    assert score >= 0.80
    
    miss, score_miss, _ = cache.lookup("Unrelated quantum gravity formulation", threshold=0.95)
    assert miss is None


def test_prompt_lookup_decoder():
    pld = PromptLookupDecoder(ngram_size=2, max_proposals=4)
    # Context: repeated sequence [10, 20, 30, 40, 50, 99, 10, 20, ...]
    ctx = [10, 20, 30, 40, 50, 99, 10, 20]
    drafts = pld.propose_draft_tokens(ctx)
    assert drafts == [30, 40, 50, 99]
    
    # Mock verify function
    def mock_verify(c, d):
        return [(True, d[0]), (True, d[1]), (False, 999)]
        
    accepted, count = pld.verify_speculative_candidates(ctx, drafts, mock_verify)
    assert count == 3
    assert accepted == [30, 40, 999]


def test_pld_integration():
    decoder = PLDIntegratedDecoder(ngram_size=2, max_proposals=3)
    prompt = "The quick brown fox jumps over the quick brown"
    
    def tokenize(s):
        mapping = {"the": 1, "quick": 2, "brown": 3, "fox": 4, "jumps": 5, "over": 6}
        return [mapping.get(w.lower(), 99) for w in s.split()]
        
    def detokenize(t):
        rev = {1: "the", 2: "quick", 3: "brown", 4: "fox", 5: "jumps", 6: "over"}
        return " " + rev.get(t[0], "unknown")
        
    def verify_batch(ctx, drafts):
        return [(True, drafts[0])]
        
    tokens_out = list(decoder.generate_with_pld(
        prompt,
        tokenize_fn=tokenize,
        detokenize_fn=detokenize,
        verify_batch_fn=verify_batch,
        max_tokens=2
    ))
    assert len(tokens_out) > 0


def test_vulkan_orchestrator():
    orchestrator = VulkanOrchestrator(model_path="nonexistent_for_test.gguf")
    gen_text = orchestrator.generate("Hello Vulkan")
    assert "Vulkan" in gen_text
    
    stream_chunks = list(orchestrator.generate_stream("Hello Vulkan Stream"))
    assert len(stream_chunks) > 0


def test_safe_math_eval_and_cache_manager():
    assert safe_math_eval("2 + 2") == 4
    assert safe_math_eval("10 * (5 - 3) / 2") == 10.0
    assert safe_math_eval("2 ** 3") == 8
    # Dangerous statements must safely return None
    assert safe_math_eval("__import__('os').system('dir')") is None
    assert safe_math_eval("open('secret.txt').read()") is None
    
    mgr = CacheManager()
    bypass_math = mgr.semantic_cache.check_procedural_bypass("what is 100 * 25?")
    assert bypass_math is not None
    assert "2500" in bypass_math
    
    bypass_time = mgr.semantic_cache.check_procedural_bypass("what is the current time?")
    assert bypass_time is not None
    assert "System Time" in bypass_time
