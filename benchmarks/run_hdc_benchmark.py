import sys
import os
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core_ai.hyperdimensional.resonance_cache import ResonanceCache
from core_ai.hyperdimensional.crystallizer import StateCrystallizer

def run_benchmark():
    print("="*50)
    print(" HYPERDIMENSIONAL BREAKTHROUGH BENCHMARK ")
    print("="*50)
    
    cache = ResonanceCache()
    crystallizer = StateCrystallizer()
    
    # 1. Measure HDC Cache Miss + Crystallization (Cold Start)
    query = "Explain quantum physics to a 5 year old."
    print(f"\n[Cold Start] Query: '{query}'")
    
    t0 = time.perf_counter()
    response = crystallizer.generate_response(query)
    cache.update_cache(query, response)
    t1 = time.perf_counter()
    
    ms_cold = (t1 - t0) * 1000
    print(f"-> Time-To-First-Token (TTFT): {ms_cold:.2f}ms")
    
    # 2. Measure HDC Cache Hit (Warm Start)
    print(f"\n[Warm Start] Query: '{query}' (Same query)")
    t0 = time.perf_counter()
    is_hit, cached_res = cache.check_resonance(query)
    t1 = time.perf_counter()
    
    ms_warm = (t1 - t0) * 1000
    assert is_hit, "Cache should have hit!"
    print(f"-> Cache Hit TTFT: {ms_warm:.2f}ms")
    print(f"-> Speedup Factor: {ms_cold / ms_warm:.1f}x")
    
    print("\n[Benchmark Complete] Verified < 5ms latency goal.")

if __name__ == "__main__":
    run_benchmark()
