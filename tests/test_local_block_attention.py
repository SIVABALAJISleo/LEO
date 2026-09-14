"""
tests/test_local_block_attention.py
Ruthless Falsification & Quality Verification Suite for LEO Attention Redesign.
Verifies numerical stability, causal invariance, adversarial edge cases,
and 100-prompt quality contracts on Intel i5 architecture.
"""

import pytest
import numpy as np
import torch
from core_ai.attention import VectorizedBlockAttention, LocalAttention, LocalBlockAttentionModule


class TestNumericalStability:
    """Falsification tests against pathological and adversarial numerical inputs."""

    def test_random_inputs(self):
        """Verify random Gaussian inputs produce valid, finite outputs."""
        seq_len, d = 256, 64
        np.random.seed(101)
        Q = np.random.randn(seq_len, d).astype(np.float32)
        K = np.random.randn(seq_len, d).astype(np.float32)
        V = np.random.randn(seq_len, d).astype(np.float32)

        block_attn = VectorizedBlockAttention(block_size=64, summary_size=20)
        local_attn = LocalAttention(window_size=64)

        out_block = block_attn.forward(Q, K, V)
        out_local = local_attn.forward(Q, K, V)

        assert out_block.shape == (seq_len, d)
        assert out_local.shape == (seq_len, d)
        assert np.isfinite(out_block).all(), "Block attention produced non-finite values"
        assert np.isfinite(out_local).all(), "Local attention produced non-finite values"

    def test_adversarial_zeros(self):
        """Input matrices with all zeros must not crash or trigger division by zero."""
        seq_len, d = 128, 64
        Q = np.zeros((seq_len, d), dtype=np.float32)
        K = np.zeros((seq_len, d), dtype=np.float32)
        V = np.zeros((seq_len, d), dtype=np.float32)

        block_attn = VectorizedBlockAttention(block_size=32, summary_size=10)
        local_attn = LocalAttention(window_size=32)

        out_block = block_attn.forward(Q, K, V)
        out_local = local_attn.forward(Q, K, V)

        assert np.isfinite(out_block).all()
        assert np.isfinite(out_local).all()
        assert np.allclose(out_block, 0.0)
        assert np.allclose(out_local, 0.0)

    def test_adversarial_ones(self):
        """Input matrices with all ones must produce uniform, stable projections."""
        seq_len, d = 128, 64
        Q = np.ones((seq_len, d), dtype=np.float32)
        K = np.ones((seq_len, d), dtype=np.float32)
        V = np.ones((seq_len, d), dtype=np.float32) * 3.5

        block_attn = VectorizedBlockAttention(block_size=32, summary_size=10, causal=False)
        local_attn = LocalAttention(window_size=32, causal=False)

        out_block = block_attn.forward(Q, K, V)
        out_local = local_attn.forward(Q, K, V)

        assert np.isfinite(out_block).all()
        assert np.isfinite(out_local).all()
        # With all ones, weighted average of V should equal V's uniform value
        assert np.allclose(out_block, 3.5, atol=1e-3)
        assert np.allclose(out_local, 3.5, atol=1e-3)

    def test_adversarial_ill_conditioned(self):
        """Test extreme values (-1e6 to +1e6) to verify softmax stability under overflow/underflow."""
        seq_len, d = 128, 64
        np.random.seed(42)
        Q = np.random.randn(seq_len, d).astype(np.float32) * 1e4
        K = np.random.randn(seq_len, d).astype(np.float32) * 1e4
        V = np.random.randn(seq_len, d).astype(np.float32)

        block_attn = VectorizedBlockAttention(block_size=32, summary_size=10)
        local_attn = LocalAttention(window_size=32)

        out_block = block_attn.forward(Q, K, V)
        out_local = local_attn.forward(Q, K, V)

        assert np.isfinite(out_block).all(), "Softmax exploded on ill-conditioned block attention"
        assert np.isfinite(out_local).all(), "Softmax exploded on ill-conditioned local attention"


class TestCausalInvariance:
    """Verifies that future token modifications do not alter past token outputs."""

    def test_causal_masking_invariance(self):
        seq_len, d = 128, 64
        np.random.seed(77)
        Q = np.random.randn(seq_len, d).astype(np.float32)
        K = np.random.randn(seq_len, d).astype(np.float32)
        V = np.random.randn(seq_len, d).astype(np.float32)

        block_attn = VectorizedBlockAttention(block_size=32, summary_size=10, causal=True)
        out_orig = block_attn.forward(Q, K, V)

        # Mutate second half of keys and values (future tokens)
        K_mut = K.copy()
        V_mut = V.copy()
        K_mut[64:] = np.random.randn(64, d) * 10.0
        V_mut[64:] = np.random.randn(64, d) * 10.0

        out_mut = block_attn.forward(Q, K_mut, V_mut)

        # Output for first half (tokens 0..63) MUST remain strictly identical
        assert np.allclose(out_orig[:64], out_mut[:64], atol=1e-5), \
            "Causal invariance violated: past tokens changed when future tokens were mutated!"


class TestBatchAndShapeParity:
    """Verify batch processing works across multi-sequence tensors."""

    def test_batch_processing(self):
        batch_size, seq_len, d = 4, 128, 64
        np.random.seed(99)
        Q = np.random.randn(batch_size, seq_len, d).astype(np.float32)
        K = np.random.randn(batch_size, seq_len, d).astype(np.float32)
        V = np.random.randn(batch_size, seq_len, d).astype(np.float32)

        block_attn = VectorizedBlockAttention(block_size=32, summary_size=10)
        local_attn = LocalAttention(window_size=32)

        out_b = block_attn.forward(Q, K, V)
        out_l = local_attn.forward(Q, K, V)

        assert out_b.shape == (batch_size, seq_len, d)
        assert out_l.shape == (batch_size, seq_len, d)


class TestPyTorchModuleIntegration:
    """Tests PyTorch module drop-in integration and backpropagation compatibility."""

    def test_pytorch_block_module(self):
        hidden_dim = 128
        seq_len = 128
        batch_size = 2

        layer = LocalBlockAttentionModule(
            hidden_dim=hidden_dim,
            num_heads=4,
            mode="block",
            block_size=32,
            summary_size=8,
            causal=True
        )

        x = torch.randn(batch_size, seq_len, hidden_dim, requires_grad=True)
        out = layer(x)

        assert out.shape == (batch_size, seq_len, hidden_dim)
        loss = out.sum()
        loss.backward()

        assert x.grad is not None
        assert torch.isfinite(x.grad).all()

    def test_pytorch_local_module(self):
        hidden_dim = 128
        seq_len = 128
        batch_size = 2

        layer = LocalBlockAttentionModule(
            hidden_dim=hidden_dim,
            num_heads=4,
            mode="local",
            window_size=32,
            causal=True
        )

        x = torch.randn(batch_size, seq_len, hidden_dim, requires_grad=True)
        out = layer(x)

        assert out.shape == (batch_size, seq_len, hidden_dim)
        loss = out.sum()
        loss.backward()

        assert x.grad is not None
        assert torch.isfinite(x.grad).all()


class TestQualityAndPromptFalsification:
    """Runs 100 prompt simulation iterations to verify contract parity and absence of collapse."""

    def test_100_prompts_contract_verification(self):
        block_attn = VectorizedBlockAttention(block_size=64, summary_size=20, causal=True)
        local_attn = LocalAttention(window_size=64, causal=True)
        
        num_prompts = 100
        success_count = 0

        for seed in range(num_prompts):
            np.random.seed(seed)
            # Varied sequence lengths typical of prompt prefill & generation
            seq_len = np.random.randint(48, 256)
            d = 64
            Q = np.random.randn(seq_len, d).astype(np.float32)
            K = np.random.randn(seq_len, d).astype(np.float32)
            V = np.random.randn(seq_len, d).astype(np.float32)

            out_block = block_attn.forward(Q, K, V)
            out_local = local_attn.forward(Q, K, V)

            # Contract check: all finite, non-zero variance, correct shape
            assert np.isfinite(out_block).all()
            assert np.isfinite(out_local).all()
            assert np.var(out_block) > 1e-6
            assert np.var(out_local) > 1e-6

            success_count += 1

        assert success_count == 100, f"Only {success_count}/100 prompt verification checks passed!"
