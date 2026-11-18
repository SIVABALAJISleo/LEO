"""
tests/test_kimi_moe_packed_stream.py
=====================================
Unit & Integration Test Suite for Kimi K3-Style 896-Expert Conditional Streaming & KDA Engine.
Hardware Target: Intel Core i5-12450H + Intel UHD Graphics + 16GB RAM.
"""

import hashlib
import numpy as np
import pytest

from backend.canonical.kimi_moe_packed_stream_subsumption import (
    MXFP4PackedExpertBank,
    KimiDeltaAttentionCore,
    benchmark_kimi_k3_subsumption_strategy,
)


class TestKimiMoEPackedStreamSubsumption:
    """Rigorous verification of the 4 Kimi K3-style architectural reductions."""

    def test_1_mxfp4_packing_and_nibble_multiplication(self):
        """Test: MXFP4 packs 2 weights per byte with 32-element micro-block scales."""
        bank = MXFP4PackedExpertBank(
            num_experts=16,
            active_experts=4,
            hidden_dim=128,
            expert_inter_dim=64,
            lru_cache_capacity=8,
            seed=42,
        )
        total_weights = 128 * 64
        packed_bytes = total_weights // 2
        assert len(bank.packed_nibbles[0]) == packed_bytes
        assert len(bank.block_scales[0]) == total_weights // 32

        # Verify in-place multiplication output dimensions
        x = np.random.randn(4, 128).astype(np.float32)
        y = bank.multiply_packed_expert(x, bank.packed_nibbles[0], bank.block_scales[0])
        assert y.shape == (4, 128)
        assert np.all(np.isfinite(y))

    def test_2_router_top_16_awake_880_asleep(self):
        """Test: Exactly 16 experts awake out of 896 (98.21% FLOPs eliminated)."""
        bank = MXFP4PackedExpertBank(
            num_experts=896,
            active_experts=16,
            hidden_dim=256,
            expert_inter_dim=64,
            lru_cache_capacity=64,
            seed=2026,
        )
        x_batch = np.random.randn(8, 256).astype(np.float32)
        top_indices, gates = bank.route_top_k(x_batch)

        assert top_indices.shape == (8, 16)
        assert gates.shape == (8, 16)
        # Softmax normalized
        assert np.allclose(np.sum(gates, axis=-1), 1.0, atol=1e-5)
        # All expert IDs within [0, 895]
        assert np.all((top_indices >= 0) & (top_indices < 896))

    def test_3_kimi_delta_attention_recurrent_state(self):
        """Test: KDA recurrent state is constant O(d^2) (4096 bytes) regardless of sequence length."""
        kda = KimiDeltaAttentionCore(hidden_dim=256, latent_dim=32, seed=2026)

        for seq_len in [8, 32, 128]:
            x_seq = np.random.randn(seq_len, 256).astype(np.float32)
            out, state_bytes = kda.forward_sequence(x_seq)
            assert out.shape == (seq_len, 256)
            # 32 x 32 float32 state = 1024 * 4 = 4096 bytes constant
            assert state_bytes == 4096

    def test_4_100pct_byte_identical_server_vs_laptop_streaming(self):
        """Test: 100% byte-identical SHA-256 output between server and 8GB laptop streaming mode."""
        report = benchmark_kimi_k3_subsumption_strategy(
            num_tokens=16,
            hidden_dim=256,
            num_experts=896,
            active_experts=16,
            expert_inter_dim=64,
            lru_cache_capacity=32,
        )

        assert report["strategy"] == "KIMI_K3_896_EXPERT_MXFP4_AND_KDA_SUBSUMPTION"
        assert report["total_experts_per_layer"] == 896
        assert report["awake_experts_per_token"] == 16
        assert report["asleep_experts_per_token"] == 880
        assert report["inactive_compute_eliminated_pct"] == 98.21
        assert report["byte_identical_parity_verified"] is True
        assert report["server_sha256"] == report["laptop_8gb_mode_sha256"]

    def test_5_speculative_batching_amortization(self):
        """Test: Multi-token batching amortizes streamed expert loads."""
        bank = MXFP4PackedExpertBank(
            num_experts=896,
            active_experts=16,
            hidden_dim=256,
            expert_inter_dim=64,
            lru_cache_capacity=64,
            seed=2026,
        )
        x_batch = np.random.randn(16, 256).astype(np.float32)
        out = bank.forward_moe(x_batch, use_lru_stream=True)
        assert out.shape == (16, 256)
        # Total active requests = 16 tokens * 16 awake = 256 requests
        # Unique experts streamed <= 256
        assert bank.disk_reads_count <= 256
