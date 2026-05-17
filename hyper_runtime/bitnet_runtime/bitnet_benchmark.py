import sys
import os
import numpy as np

# Allow running from project root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from hyper_runtime.bitnet_runtime.bitlinear import BitLinear
from hyper_runtime.bitnet_runtime.simd_kernels import CPUKernelOptimizer
from hyper_runtime.bitnet_runtime.quantized_kv import QuantizedKVCache

def run_benchmark():
    print("=" * 70)
    print("  HYPERCORE RUNTIME — MODULE 7: BITNET LOW-BIT RUNTIME")
    print("=" * 70)
    
    in_features = 4096
    out_features = 4096
    seq_len = 128
    batch_size = 1
    
    # 1. Initialize BitLinear Layer
    print("\n[1/3] Initializing 1.58-bit (Ternary) Linear Layer...")
    layer = BitLinear(in_features, out_features)
    layer.quantize_weights()
    print("  Weights successfully quantized to {-1, 0, 1}.")
    
    # Generate mock FP32 activations
    np.random.seed(42)
    activations = np.random.randn(batch_size, seq_len, in_features).astype(np.float32)
    
    # Run forward pass
    out_f, telemetry = layer.forward(activations)
    
    print("\n  [BitLinear Forward Pass Telemetry]")
    print(f"    Original Weights Memory: {telemetry['original_memory_mb']:.2f} MB")
    print(f"    Ternary Weights Memory:  {telemetry['weight_memory_mb']:.2f} MB")
    print(f"    Compression Ratio:       {telemetry['compression_ratio']:.2f}x")
    print(f"    Execution Operations:    {telemetry['operations_type']} (Avoiding FP32 MACs)")
    
    # 2. Simulate CPU Kernel Packing & Alignment
    print("\n[2/3] CPU Memory Alignment & SIMD Packing...")
    optimizer = CPUKernelOptimizer()
    packed_weights = optimizer.pack_ternary_weights(layer.weight_quantized)
    aligned_info = optimizer.align_memory(layer.weight_quantized)
    
    # Theoretical packing ratio for ternary (2 bits) -> 4 weights per byte
    packed_mb = packed_weights.nbytes / (1024 * 1024)
    print(f"    Packed SIMD Array Memory: {packed_mb:.2f} MB (Theoretical 4x reduction over INT8)")
    print(f"    Memory Alignment (AVX512): {aligned_info['alignment']}-byte boundaries")
    
    # 3. Quantized KV Cache
    print("\n[3/3] Initializing INT8 Quantized KV Cache...")
    kv_cache = QuantizedKVCache(max_seq_len=8192, num_heads=32, head_dim=128, bits=8)
    
    # Mock K, V generation
    k_states = np.random.randn(seq_len, 32, 128).astype(np.float32)
    v_states = np.random.randn(seq_len, 32, 128).astype(np.float32)
    
    kv_cache.append(k_states, v_states)
    kv_metrics = kv_cache.get_memory_footprint_mb()
    
    print("\n  [KV Cache Telemetry (Capacity: 8192 tokens)]")
    print(f"    FP32 Equivalent Memory: {kv_metrics['fp32_equivalent_mb']:.2f} MB")
    print(f"    INT8 Quantized Memory:  {kv_metrics['quantized_cache_mb']:.2f} MB")
    print(f"    Memory Reduction Ratio: {kv_metrics['compression_ratio']:.2f}x")
    
    print("\n" + "=" * 70)
    print("  MODULE 7 SUMMARY")
    print("=" * 70)
    print("The BitNet runtime slashes memory bandwidth by quantizing weights to 1.58 bits")
    print("and replacing floating-point matrix multiplications with integer additions.")

if __name__ == "__main__":
    run_benchmark()
