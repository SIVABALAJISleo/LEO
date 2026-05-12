import time
import numpy as np
from bitnet_runtime import BitNetRuntime

def run_benchmark():
    print("Running BitNet CPU Benchmark...")
    M, N, K = 32, 4096, 4096 
    
    A_float = np.random.randn(M, K).astype(np.float32)
    W_float = np.random.randn(N, K).astype(np.float32)
    W_ternary = np.sign(np.round(W_float)).astype(np.int8) 
    
    runtime = BitNetRuntime()
    A_q, scale = runtime.simulate_quantization(A_float)
    
    print(f"Matrix size: {M}x{K} * {K}x{N}")
    
    _ = runtime.linear(A_q, W_ternary)
    
    start = time.time()
    iters = 100
    for _ in range(iters):
        _ = runtime.linear(A_q, W_ternary)
    end = time.time()
    
    ms_per_iter = ((end - start) / iters) * 1000
    print(f"Average BitLinear latency: {ms_per_iter:.2f} ms")
    
    fp16_mem = (N * K * 2) / (1024**2)
    bitnet_mem = (N * K * 0.25) / (1024**2) 
    print(f"Weight Memory (FP16): {fp16_mem:.2f} MB")
    print(f"Weight Memory (Ternary Packed): {bitnet_mem:.2f} MB")
    print(f"Memory Reduction: {fp16_mem/bitnet_mem:.1f}x")

if __name__ == "__main__":
    run_benchmark()
