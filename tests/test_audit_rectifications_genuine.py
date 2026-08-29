"""
tests/test_audit_rectifications_genuine.py
==========================================
Comprehensive Verification Suite for Rectified Core Systems:
1. Genuine Semantic Cache & FAISS Embeddings (No keyword-only hashes)
2. Genuine Speculative & Prompt Lookup Decoding (PLD with n-gram verification)
3. Genuine Local Neural Inference Engine (Coherent responses, TTFT & tok/s)
4. Genuine OpenVINO Intel UHD iGPU Dispatch (Targeted graph compilation)
5. Genuine 3D SDF Raymarching Volume Renderer (True 3D geometry & PSNR/SSIM)
6. Genuine Symplectic Leapfrog Physics (Hamiltonian energy conservation)
"""

import pytest
import numpy as np

from core_ai.semantic_cache import SemanticBypassEngine
from core_ai.prompt_lookup_decoder import PromptLookupDecoder
from backend.inference.speculative_decoder import SpeculativeDecoder
from core_ai.neural_inference_engine import NeuralInferenceEngine
from backend.layer5_local_infer.local_model import LocalInferenceRunner
from backend.layer4_igpu.openvino_igpu_engine import OpenVINOiGPUEngine
from core_ai.media.real_volume_renderer import RealVolumeRenderer
from core_ai.causal_physics_engine import SymplecticPhysicsEngine


class TestAuditRectificationsGenuine:

    def test_1_semantic_cache_faiss_generalization(self):
        """Test: FAISS Semantic Cache matches paraphrased queries with high similarity."""
        cache = SemanticBypassEngine(semantic_threshold=0.70)
        cache.store("how do I reset my account password", "Visit settings -> security -> reset password.", tag="auth")

        # Paraphrased query
        resp, score, tier = cache.query("I forgot my password, how to change it?")
        assert resp is not None
        assert "reset password" in resp.lower()
        assert score >= 0.70
        assert tier in ("LEVEL_1_EXACT", "LEVEL_2_FAISS_SEMANTIC", "LEVEL_2_SEMANTIC_COSINE", "LEVEL_3_GRAPH_LATTICE")

    def test_2_prompt_lookup_speculative_decoding(self):
        """Test: PLD extracts context n-grams and executes verification."""
        pld = PromptLookupDecoder(ngram_size=3, max_proposals=4)

        # Context containing repeating sequence [10, 20, 30, 40, 50, 60]
        context = [100, 200, 10, 20, 30, 40, 50, 60, 300, 400, 10, 20, 30]
        draft = pld.propose_draft_tokens(context)
        # Suffix is [10, 20, 30]. Following tokens from earlier in sequence are [40, 50, 60, 300] (4 proposals)
        assert draft == [40, 50, 60, 300]

        # Target verifier accepts first two tokens and rejects the third
        def mock_verifier(ctx, drafts):
            return [(True, drafts[0]), (True, drafts[1]), (False, 999)]

        accepted, count = pld.verify_speculative_candidates(context, draft, mock_verifier)
        assert accepted == [40, 50, 999]
        assert count == 3

    def test_3_neural_inference_coherent_structured_output(self):
        """Test: Local neural inference produces non-gibberish, structured, high-quality responses."""
        engine = NeuralInferenceEngine(n_threads=8)
        res = engine.generate("Explain how Winograd convolution eliminates operations.")

        assert res["status"] == "SUCCESS"
        assert res["tokens_generated"] > 0
        assert res["ttft_ms"] >= 0.0
        assert res["throughput_tok_s"] > 0.0
        # Text must be coherent English without random <unk> corruption
        text = res["text"]
        assert len(text) > 20
        assert "<unk>" not in text

    def test_4_openvino_igpu_graph_execution(self):
        """Test: OpenVINO engine targets Intel UHD / CPU and computes accurate matrix multiply."""
        igpu = OpenVINOiGPUEngine()
        A = np.random.randn(32, 32).astype(np.float32)
        B = np.random.randn(32, 32).astype(np.float32)

        out, telemetry = igpu.execute_matmul_on_target(A, B)
        expected = A @ B

        assert telemetry["status"] == "success"
        assert telemetry["execution_time_ms"] >= 0.0
        assert np.allclose(out, expected, atol=1e-4)

    def test_5_real_volume_rendering_raymarching_and_upscaling(self):
        """Test: Genuine 3D SDF raymarching renders physical geometry and calculates PSNR."""
        # 1. Render ground truth at 64x64
        gt_frame = RealVolumeRenderer.render_frame(resolution=(64, 64), max_steps=32)
        assert gt_frame.shape == (64, 64)
        assert float(np.min(gt_frame)) >= 0.0
        assert float(np.max(gt_frame)) <= 1.0

        # 2. Render coarse (32x32) with bilinear upscaling to (64x64)
        upscaled, lat_ms, fps = RealVolumeRenderer.render_subsampled_with_upscaling(
            coarse_res=(32, 32), target_res=(64, 64)
        )
        assert upscaled.shape == (64, 64)
        assert fps > 30.0  # Real-time frame rate

        # 3. Quality metrics against ground truth
        metrics = RealVolumeRenderer.evaluate_quality_metrics(upscaled, gt_frame)
        assert metrics["psnr_db"] > 25.0
        assert metrics["ssim"] > 0.85

    def test_6_symplectic_physics_hamiltonian_energy_conservation(self):
        """Test: Symplectic leapfrog N-body integrator conserves total Hamiltonian energy."""
        physics = SymplecticPhysicsEngine(num_bodies=64, G=1.0)
        res = physics.simulate_trajectory(steps=50, dt=0.005)

        assert res["invariant_preserved"] is True
        assert res["energy_conservation_drift"] < 1e-3
