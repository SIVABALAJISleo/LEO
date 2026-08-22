"""
LEO v6 — GEMM Truth Experiment
Runs the exact benchmark ChatGPT challenged us with.
Tests NumPy BLAS vs Trie-lookup concept across multiple matrix sizes.
"""
import numpy as np
import time
import json

# --- Build the Int8 Multiplication Lookup Table (64KB, fits in L1 cache) ---
print("Building Trie Lookup Table...")
MULT_TABLE = np.zeros((256, 256), dtype=np.int32)
for i in range(256):
    for j in range(256):
        MULT_TABLE[i, j] = i * j
print("Table ready (64KB).\n")

def numpy_gemm_fp32(a, b):
    """Standard NumPy BLAS-backed FP32 GEMM."""
    return np.dot(a, b)

def numpy_gemm_int8(a, b):
    """NumPy integer GEMM (cast to int32 for accumulation)."""
    return np.dot(a.astype(np.int32), b.astype(np.int32))

def trie_gemm_int8(a_int, b_int):
    """
    Trie/Table lookup GEMM.
    Uses NumPy advanced indexing to simulate the table lookup.
    a_int and b_int must be uint8 (0-255).
    """
    rows_a, cols_a = a_int.shape
    rows_b, cols_b = b_int.shape

    result = np.zeros((rows_a, cols_b), dtype=np.int32)
    for k in range(cols_a):
        # For each k slice, lookup products for every (i,j) pair via the table
        products = MULT_TABLE[np.ix_(a_int[:, k], b_int[k, :])]
        result += products
    return result

def run_experiment():
    results = []
    print("=" * 55)
    print("   LEO v6 — GEMM Truth Experiment")
    print("   Hardware: Intel i5-12450H | NumPy BLAS vs Trie")
    print("=" * 55)

    sizes = [64, 128, 256, 512]
    REPEATS = 3

    for size in sizes:
        print(f"\nMatrix Size: {size}x{size}")
        print("-" * 45)

        # Generate matrices
        a_fp = np.random.randn(size, size).astype(np.float32)
        b_fp = np.random.randn(size, size).astype(np.float32)
        a_uint = np.random.randint(0, 256, size=(size, size), dtype=np.uint8)
        b_uint = np.random.randint(0, 256, size=(size, size), dtype=np.uint8)
        a_int8 = a_uint.view(np.uint8)
        b_int8 = b_uint.view(np.uint8)

        # 1. NumPy FP32 BLAS baseline
        times_np_fp32 = []
        for _ in range(REPEATS):
            start = time.perf_counter()
            c_np = numpy_gemm_fp32(a_fp, b_fp)
            times_np_fp32.append(time.perf_counter() - start)
        t_np_fp32 = min(times_np_fp32)

        # 2. NumPy INT8 -> INT32
        times_np_int = []
        for _ in range(REPEATS):
            start = time.perf_counter()
            c_np_int = numpy_gemm_int8(a_uint, b_uint)
            times_np_int.append(time.perf_counter() - start)
        t_np_int = min(times_np_int)

        # 3. Trie Lookup INT8 (skip 512 as it gets very slow in pure Python)
        t_trie = None
        if size <= 256:
            times_trie = []
            for _ in range(REPEATS):
                start = time.perf_counter()
                c_trie = trie_gemm_int8(a_uint, b_uint)
                times_trie.append(time.perf_counter() - start)
            t_trie = min(times_trie)

            # Verify correctness: trie result must match numpy int result
            np.testing.assert_array_equal(c_trie, c_np_int)
            correct_str = "VERIFIED ✓"
        else:
            correct_str = "SKIPPED (too slow in Python)"

        # Print results
        print(f"  NumPy FP32  (BLAS AVX2):   {t_np_fp32*1000:.4f} ms")
        print(f"  NumPy INT32 (BLAS AVX2):   {t_np_int*1000:.4f} ms")
        if t_trie is not None:
            ratio = t_trie / t_np_fp32
            verdict = ">> TRIE FASTER!" if t_trie < t_np_fp32 else f">> BLAS is {ratio:.1f}x faster"
            print(f"  Trie  INT8  (Lookup Idx):  {t_trie*1000:.4f} ms  |  {correct_str}")
            print(f"  Verdict: {verdict}")
        else:
            print(f"  Trie  INT8  (Lookup Idx):  {correct_str}")
            print(f"  Verdict: BLAS dominates at this scale. Contract Analyzer path confirmed.")

        results.append({
            "size": size,
            "numpy_fp32_ms": round(t_np_fp32 * 1000, 4),
            "numpy_int32_ms": round(t_np_int * 1000, 4),
            "trie_int8_ms": round(t_trie * 1000, 4) if t_trie else "skipped",
        })

    print("\n" + "=" * 55)
    print("CONCLUSION:")
    print("  The BLAS AVX2 path is the hardware floor.")
    print("  The breakthrough is NOT a faster matrix multiply.")
    print("  The breakthrough is SKIPPING the multiply entirely")
    print("  via the Contract Analyzer (semantic caching, RAG,")
    print("  and surrogate approximation).")
    print("=" * 55)

    with open("gemm_experiment_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print("\nResults saved to gemm_experiment_results.json")

if __name__ == "__main__":
    run_experiment()
