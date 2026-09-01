# 🏛️ HYPER-100: Academic Research & Prior Art

## 1. Prior-Art Foundations (1980s -> Present)

1. **Randomized SVD Matrix Factorization**
   - _Halko, Martinsson, & Tropp (2011)_: "Finding Structure with Randomness: Probabilistic Algorithms for Constructing Approximate Matrix Decompositions", _SIAM Review_.
   - _Impact on HYPER:_ Reduces dense $O(M N K)$ GEMM to $O(M N k)$ with tight spectral bounds.
2. **1-Bit Large Language Models (BitNet b1.58)**
   - _Wang et al. (2024)_: "The Era of 1-bit LLMs: All Large Language Models are in 1.58 Bits", _arXiv:2402.17764_.
   - _Impact on HYPER:_ Eliminates floating-point multipliers, executing inference entirely via addition lookups.
3. **Sublinear Sparse Fourier Transform**
   - _Hassanieh, Indyk, Katabi, & Price (2012)_: "Nearly Optimal Sublinear Sparse Fourier Transform", _ACM-SIAM SODA_.
   - _Impact on HYPER:_ Reduces Fourier transform complexity from $O(N \log N)$ to $O(K \log N)$.
4. **Fast Multipole Method for Particle Simulations**
   - _Greengard & Rokhlin (1987)_: "A Fast Algorithm for Particle Simulations", _Journal of Computational Physics_.
   - _Impact on HYPER:_ Reduces astrodynamic $N$-body interactions from $O(N^2)$ to $O(N)$.
5. **Speculative Decoding**
   - _Leviathan, Kalman, & Matias (2023)_: "Fast Inference from Transformers via Speculative Decoding", _ICML_.
   - _Impact on HYPER:_ Bypasses autoregressive sequential bottlenecks on consumer CPUs.
