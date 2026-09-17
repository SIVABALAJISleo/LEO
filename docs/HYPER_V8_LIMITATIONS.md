# HYPER v8 Known Limitations & Negative Results

Scientific progress demands documenting when, where, and why optimizations fail. In accordance with the non-negotiable scientific rules of LEO/HYPER, the following limitations are recorded.

---

## 1. Overhead of Cryptographic Hashing for Small Problem Sizes
- **Mechanism**: Exact caching relies on SHA-256 digests of input tensors.
- **Limitation**: For small matrices ($N \le 64$), computing SHA-256 over input buffers takes $\approx 0.22$ ms, whereas full numpy AVX2 matrix multiplication takes only $\approx 0.012$ ms.
- **Result**: Exact caching is $\approx 20\times$ **slower** than full recomputation on tiny problems ($N \le 64$).
- **Rule**: Caching is only cost-effective when the expected execution time exceeds the digest calculation time ($\approx N \ge 128$).

---

## 2. Sparse GEMM Break-Even Threshold
- **Mechanism**: Compressed Sparse Row (CSR) matrix multiplication via SciPy.
- **Limitation**: At 90% sparsity for small to medium matrices ($N \le 512$), modern CPU vector engines (AVX2/FMA) process contiguous dense memory so efficiently that CSR pointer-chasing and index indirection overhead make sparse multiplication slower ($0.16\times$ to $0.53\times$ speedup, i.e., a slowdown).
- **Rule**: Sparse representation must not be deployed unless matrix sparsity exceeds $98\%$ to $99.5\%$ or $N \ge 2048$.

---

## 3. Intel UHD iGPU Unblocked Kernel Bound
- **Mechanism**: OpenCL Zero-Copy GEMM kernel on 48 Execution Units.
- **Limitation**: Intel Core i5-12450H CPU possesses high single-thread clock speeds, 8 physical cores, and multi-megabyte L3 caches running optimized Intel MKL / OpenBLAS. In contrast, the Intel UHD iGPU relies on shared DDR5 memory without dedicated high-bandwidth VRAM. A simple unblocked OpenCL kernel runs $10\times$ to $30\times$ slower than the multi-threaded CPU.
- **Rule**: Do not offload dense GEMM to Intel UHD iGPU unless using tiled sub-group block reads and register reuse kernels.

---

## 4. Rank Factorization Break-Even Boundary
- **Mechanism**: Low-rank factored evaluation $U \times (V \times B)$ with rank $r$.
- **Limitation**: At $N = 256$, when rank $r > 50$, evaluating two successive matrix multiplications ($N \times r$ by $r \times N$, then $N \times N$) requires more arithmetic operations and memory traffic than a single dense $N \times N \times N$ multiply. At $r = 64$, speedup drops to $0.97\times$, and at $r = 128$, it is a $0.76\times$ slowdown.
- **Rule**: Factored low-rank shortcut is strictly guarded by the condition $r < N / 4$.

---

## 5. Decision & Analysis Overhead on Random Dense Inputs
- **Mechanism**: When inputs are 100% random Gaussian dense matrices with no coherence or repetition, the selector tests cache, residual, and sparsity hypotheses before concluding no shortcut exists.
- **Limitation**: This decision process introduces an overhead of $1.6$ ms to $70$ ms depending on matrix size.
- **Mitigation**: Future revisions should implement fast heuristics (e.g. sampling 1% of entries) before executing full change detection.
