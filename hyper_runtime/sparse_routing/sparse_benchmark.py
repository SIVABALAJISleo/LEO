import sys
import os
import json
import numpy as np

# Allow running from project root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from hyper_runtime.sparse_routing.sparse_router import SparseIntelligenceRouter

def run_benchmark():
    print("=" * 70)
    print("  HYPERCORE RUNTIME — MODULE 4: SPARSE INTELLIGENCE ROUTER")
    print("=" * 70)
    
    hidden_dim = 256
    total_layers = 12
    router = SparseIntelligenceRouter(hidden_dim=hidden_dim, total_layers=total_layers)
    
    print("\n[Executing Sparse Workload Routines]")
    print("-" * 70)
    
    # Generate mock hidden states: [batch_size, seq_len, hidden_dim]
    np.random.seed(42)
    
    test_cases = [
        {
            "desc": "Standard Mixed Entropy Workload",
            "batch_size": 1,
            "seq_len": 128,
            "data": np.random.randn(1, 128, hidden_dim).astype(np.float32)
        },
        {
            "desc": "High Entropy / Highly Novel Workload",
            "batch_size": 1,
            "seq_len": 128,
            "data": np.random.randn(1, 128, hidden_dim).astype(np.float32) * 5.0 # Higher variance
        },
        {
            "desc": "Low Entropy / Highly Repetitive Workload",
            "batch_size": 1,
            "seq_len": 128,
            "data": np.ones((1, 128, hidden_dim)).astype(np.float32) + (np.random.randn(1, 128, hidden_dim).astype(np.float32) * 0.01)
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\nWorkload #{i}: {test['desc']}")
        
        metrics = router.route_execution(test["data"])
        
        print(f"  Token Merging (ToMe) Sparsity: {metrics['tome_sparsity']*100:.1f}%")
        print(f"  Entropy Gating Sparsity:       {metrics['gating_sparsity']*100:.1f}%")
        print(f"  Mixture-of-Experts Sparsity:   {metrics['moe_sparsity']*100:.1f}%")
        print(f"  Adaptive Depth Exit Layer:     {metrics['exit_layer']} / {total_layers}")
        print(f"  Depth/Layer Sparsity:          {metrics['depth_sparsity']*100:.1f}%")
        print(f"  => TOTAL COMPUTE AVOIDED:      {metrics['total_compute_avoided_ratio']*100:.2f}%")
        
    print("\n" + "=" * 70)
    print("  MODULE 4 TELEMETRY SUMMARY")
    print("=" * 70)
    print("Sparse Intelligence routing compounds savings multiplicatively by merging tokens,")
    print("skipping FFN blocks, routing only to top-k experts, and exiting early.")

if __name__ == "__main__":
    run_benchmark()
