import sys
import os
import time
import numpy as np

# Allow running from project root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from hyper_runtime.operator_fusion.lazy_tensor import LazyTensor
from hyper_runtime.operator_fusion.fusion_compiler import FusionCompiler

def run_benchmark():
    print("=" * 70)
    print("  HYPERCORE RUNTIME — MODULE 12: OPERATOR FUSION ENGINE")
    print("=" * 70)
    
    compiler = FusionCompiler()
    
    # 4Kx4K tensor (approx 64MB)
    shape = (4096, 4096)
    np.random.seed(42)
    raw_data = np.random.randn(*shape).astype(np.float32)
    weight = np.random.randn(*shape).astype(np.float32)
    bias = np.random.randn(*shape).astype(np.float32)
    
    print(f"\n[1/2] Defining Lazy Computation Graph")
    print("-" * 70)
    
    x = LazyTensor(raw_data)
    w = LazyTensor(weight)
    b = LazyTensor(bias)
    
    # Typical sequence: x = x * w + b, then ReLU
    # Normally this allocates 3 intermediate 64MB tensors
    computation_graph = (x * w + b).relu()
    
    print(f"  Operations in Graph: {[op[0] for op in computation_graph.operations]}")
    
    print(f"\n[2/2] Compiling and Executing Fused Graph")
    print("-" * 70)
    
    # Baseline Naive Execution
    t0 = time.perf_counter()
    baseline_result = computation_graph.realize()
    t1 = time.perf_counter()
    
    # Fused Execution
    t2 = time.perf_counter()
    fused_result, metrics = compiler.compile_and_execute(computation_graph)
    t3 = time.perf_counter()
    
    assert np.allclose(baseline_result, fused_result), "Fused execution mismatch!"
    
    print(f"  Naive Latency:          {(t1-t0):.4f}s")
    print(f"  Fused Latency:          {(t3-t2):.4f}s")
    print(f"  Intermediate Allocations Avoided: {metrics['operations_fused'] - 1}")
    print(f"  Memory Bandwidth Saved: {metrics['bandwidth_saved_mb']:.2f} MB")
    
    print("\n" + "=" * 70)
    print("  MODULE 12 SUMMARY")
    print("=" * 70)
    print("Operator fusion intercepts eager execution and combines multiple element-wise")
    print("operations into a single pass. This prevents thrashing DRAM with intermediate")
    print("tensor writes, dramatically reducing bandwidth constraints.")

if __name__ == "__main__":
    run_benchmark()
