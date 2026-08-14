# real_benchmark.py
import time
from core_ai.custom_kernels import RealNativeEngine

engine = RealNativeEngine()
prompt = "Explain quantum computing in one sentence."

print("Starting REAL benchmark...")
start_time = time.time()

# Generate 100 tokens
output = engine.generate(prompt, max_tokens=100)

elapsed = time.time() - start_time
tps = 100 / elapsed

print(f"\n--- REAL BENCHMARK RESULTS ---")
print(f"Time: {elapsed:.2f}s")
print(f"Throughput: {tps:.2f} Tokens/Second")
print(f"Output: {output}")
print("------------------------------")
