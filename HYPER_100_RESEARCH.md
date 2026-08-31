# 🏛️ HYPER-100: Academic Research & Prior Art

## 1. Prior-Art Foundations (1980s -> Present)

1. **Randomized SVD Matrix Factorization**
   - *Halko, Martinsson, & Tropp (2011)*: "Finding Structure with Randomness: Probabilistic Algorithms for Constructing Approximate Matrix Decompositions", *SIAM Review*.
   - *Impact on HYPER:* Reduces dense $O(M N K)$ GEMM to $O(M N k)$ with tight spectral bounds.
2. **1-Bit Large Language Models (BitNet b1.58)**
   - *Wang et al. (2024)*: "The Era of 1-bit LLMs: All Large Language Models are in 1.58 Bits", *arXiv:2402.17764*.
   - *Impact on HYPER:* Eliminates floating-point multipliers, executing inference entirely via addition lookups.
3. **Sublinear Sparse Fourier Transform**
   - *Hassanieh, Indyk, Katabi, & Price (2012)*: "Nearly Optimal Sublinear Sparse Fourier Transform", *ACM-SIAM SODA*.
   - *Impact on HYPER:* Reduces Fourier transform complexity from $O(N \log N)$ to $O(K \log N)$.
4. **Fast Multipole Method for Particle Simulations**
   - *Greengard & Rokhlin (1987)*: "A Fast Algorithm for Particle Simulations", *Journal of Computational Physics*.
   - *Impact on HYPER:* Reduces astrodynamic $N$-body interactions from $O(N^2)$ to $O(N)$.
5. **Speculative Decoding**
   - *Leviathan, Kalman, & Matias (2023)*: "Fast Inference from Transformers via Speculative Decoding", *ICML*.
   - *Impact on HYPER:* Bypasses autoregressive sequential bottlenecks on consumer CPUs.
