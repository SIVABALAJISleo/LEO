import time
import os
import sys

def profile_startup_and_memory():
    print("[PERFORMANCE PROFILER] Profiling Python Process & Initial Memory Footprint...")
    start_time = time.time()
    import backend.main
    startup_latency = (time.time() - start_time) * 1000
    print(f"[PERFORMANCE PROFILER] Cold Startup Time: {startup_latency:.2f}ms")

    try:
        import psutil
        process = psutil.Process(os.getpid())
        mem_mb = process.memory_info().rss / (1024 * 1024)
        print(f"[PERFORMANCE PROFILER] RSS Memory Footprint: {mem_mb:.2f} MB")
    except ImportError:
        print("[PERFORMANCE PROFILER] psutil not installed, memory profiling skipped.")

if __name__ == "__main__":
    profile_startup_and_memory()
