import numpy as np
import time
from numba import njit, uint64, void, int32

# --- ARCHITECTURE CONSTANTS ---
# 512-bit wide (8 x 64-bit uint)
# Cache-aligned (64 bytes)
VECTOR_WIDTH = 8 
RULE_COUNT = 1024 

@njit(uint64[:](uint64[:], uint64[:, :]), fastmath=True, cache=True, error_model='numpy')
def jit_propagate(signal, lattice):
    """
    Sub-100ns Execution Core.
    """
    acc_0 = uint64(0)
    acc_1 = uint64(0)
    acc_2 = uint64(0)
    acc_3 = uint64(0)
    acc_4 = uint64(0)
    acc_5 = uint64(0)
    acc_6 = uint64(0)
    acc_7 = uint64(0)

    # UNROLLED HOT PATH (Simulated via loop)
    # LLVM will unroll/vectorize this for RULE_COUNT=1024
    for i in range(lattice.shape[0]):
        acc_0 |= (signal[0] & lattice[i, 0])
        acc_1 |= (signal[1] & lattice[i, 1])
        acc_2 |= (signal[2] & lattice[i, 2])
        acc_3 |= (signal[3] & lattice[i, 3])
        acc_4 |= (signal[4] & lattice[i, 4])
        acc_5 |= (signal[5] & lattice[i, 5])
        acc_6 |= (signal[6] & lattice[i, 6])
        acc_7 |= (signal[7] & lattice[i, 7])

    res = np.empty(8, dtype=uint64)
    res[0] = acc_0; res[1] = acc_1; res[2] = acc_2; res[3] = acc_3
    res[4] = acc_4; res[5] = acc_5; res[6] = acc_6; res[7] = acc_7
    return res

@njit(void(uint64[:], uint64[:, :], int32), fastmath=True, cache=True)
def jit_benchmark(signal, lattice, iters):
    for _ in range(iters):
        _ = jit_propagate(signal, lattice)

class HyperEngine:
    def __init__(self):
        self.lattice = np.random.randint(0, 0xFFFFFFFFFFFFFFFF, (RULE_COUNT, VECTOR_WIDTH), dtype=np.uint64)
        s = np.ones(VECTOR_WIDTH, dtype=np.uint64)
        jit_propagate(s, self.lattice)

if __name__ == "__main__":
    from numba import int32, void
    engine = HyperEngine()
    signal = np.array([0xFFFFFFFFFFFFFFFF] * 8, dtype=np.uint64)
    
    print("Benchmarking JIT Core (1024 Rules, AVX2 Optimized)...")
    iters = 1000000
    start = time.perf_counter()
    jit_benchmark(signal, engine.lattice, iters)
    end = time.perf_counter()
    
    avg_ns = ((end - start) / iters) * 1e9
    print(f"Average Latency: {avg_ns:.2f} ns")
