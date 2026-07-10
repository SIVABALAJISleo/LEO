"""
leo_infinity_kernels — Example: HuggingFace Ternary LUT Integration

Demonstrates wrapping a HuggingFace transformer model's linear layers
with LEO's ternary LUT matmul for multiplication-free CPU inference.

Usage:
    pip install leo_infinity_kernels[huggingface]
    python huggingface_integration.py
"""

from __future__ import annotations

import numpy as np

# This example works without torch/transformers installed — it mocks the concept.
# When the extras are installed, swap in real model weights.


def demo_ternary_replacement():
    """Show how a standard linear layer's matmul can be replaced."""
    from leo_infinity_kernels import TernaryLUTEngine

    engine = TernaryLUTEngine(isa_level="AVX2")

    # Simulate a transformer linear layer: weight (768, 768) + activation (768,)
    print("Simulating a transformer linear layer (768 x 768)...")
    weight = np.random.randn(768, 768).astype(np.float64)
    activation = np.random.randn(768).astype(np.float64)

    # Standard FP64 matmul
    import time
    t0 = time.perf_counter()
    standard_out = weight @ activation
    std_ms = (time.perf_counter() - t0) * 1000

    # Ternary LUT matmul (multiplication-free)
    t0 = time.perf_counter()
    ternary_out = engine.execute_lut_matmul(weight, activation)
    tern_ms = (time.perf_counter() - t0) * 1000

    # Accuracy check (ternary is lossy — but fast)
    mae = np.mean(np.abs(standard_out - ternary_out))

    print(f"  Standard matmul:  {std_ms:.3f} ms")
    print(f"  Ternary LUT:      {tern_ms:.3f} ms")
    print(f"  Mean Abs Error:   {mae:.4f} (expected: lossy quantization)")
    print(f"  Multiply ops avoided: {engine.get_stats()['total_multiply_ops_avoided']:,}")
    print()
    print("Integration pattern for HuggingFace models:")
    print("  1. Load model: model = AutoModel.from_pretrained('bert-base-uncased')")
    print("  2. Extract weight: W = model.encoder.layer[0].attention.self.query.weight.detach().numpy()")
    print("  3. Replace forward: output = engine.execute_lut_matmul(W, hidden_states)")
    print("  4. This eliminates all multiplications in the attention query projection.")
    print()
    print("For batch inference, use engine.execute_lut_matmul_batch(W, batch_activations)")


if __name__ == "__main__":
    print("=" * 60)
    print("  LEO Infinity Kernels — HuggingFace Integration Example")
    print("=" * 60)
    demo_ternary_replacement()
