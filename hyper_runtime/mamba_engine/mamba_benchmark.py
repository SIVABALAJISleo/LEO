import sys
import os
import time
import numpy as np

# Allow running from project root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from hyper_runtime.mamba_engine.mamba_layer import MambaLayer

def run_benchmark():
    print("=" * 70)
    print("  HYPERCORE RUNTIME — MODULE 10: MAMBA / SSM ENGINE")
    print("=" * 70)
    
    d_model = 1024
    d_state = 16
    layer = MambaLayer(d_model=d_model, d_state=d_state, expand=2)
    d_inner = d_model * 2
    
    test_lengths = [128, 1024, 8192, 32768]
    batch_size = 1
    
    print("\n[Executing State Space Sequence Processing]")
    print("-" * 70)
    
    for seq_len in test_lengths:
        print(f"\nSequence Length: {seq_len:,} tokens")
        
        # Mock Input
        np.random.seed(42)
        x_seq = np.random.randn(batch_size, seq_len, d_inner).astype(np.float32)
        
        t0 = time.perf_counter()
        out_seq, metrics = layer.forward_sequence(x_seq)
        t1 = time.perf_counter()
        
        print(f"  Latency:                  {(t1-t0):.3f}s")
        print(f"  Recurrent State Memory:   {metrics['ssm_state_mb']:.4f} MB (Constant)")
        print(f"  Transformer KV Equiv:     {metrics['transformer_kv_equivalent_mb']:.2f} MB (O(N))")
        
        # Calculate reduction factor (ensure we don't divide by zero if state is tiny)
        reduction = metrics['transformer_kv_equivalent_mb'] / max(1e-6, metrics['ssm_state_mb'])
        print(f"  Memory Footprint Savings: {reduction:,.1f}x")
        
    print("\n" + "=" * 70)
    print("  MODULE 10 SUMMARY")
    print("=" * 70)
    print("Mamba cleanly eliminates quadratic memory explosion for long sequences.")
    print("While a Transformer's KV cache grows linearly with context length,")
    print("the SSM recurrent state size remains strictly constant (O(1)).")

if __name__ == "__main__":
    run_benchmark()
