# HYPER: Autonomous Algorithm Discovery Specification

## 1. Beyond Hardcoded Rules
Most compiler and runtime optimizers are limited to fixed, hand-coded heuristics (e.g. unroll loop by 4, tile by 64).
**HYPER Algorithm Discovery** (`algorithm_discovery/`) systematically searches for alternative algorithms with lower asymptotic complexity or better hardware alignment.

---

## 2. The Algorithmic Transformation Catalog

```mermaid
graph LR
    O_N2[O(N^2) All-Pairs] -->|Spatial Octree| O_NLOGN[O(N log N) Barnes-Hut]
    O_NLOGN_FFT[O(N log N) Dense FFT] -->|Frequency Sparsity| O_KLOGN[O(k log N) Sublinear sFFT]
    O_MNK[O(M*N*K) Dense GEMM] -->|Spectral Decay| O_LR[O(r*(M+N)*K) Low-Rank SVD]
    MC[O(1/eps^2) Monte Carlo] -->|Sobol Sequences| QMC[O(1/eps) Quasi-Monte Carlo]
    SORT[O(N log N) Full Sort] -->|Top-K Query| SELECT[O(N) QuickSelect / Argpartition]
```

---

## 3. Autonomous Evolutionary Optimization Loop

The evolutionary discovery engine continuously explores the multi-dimensional parameter space:
1. **GENERATE**: Initial population generated from templates and historical strategy memory.
2. **COMPILE**: Lowered to Universal Computation IR with layout alignment.
3. **TEST & VERIFY**: Evaluated by independent verifiers against frozen contracts.
4. **BENCHMARK**: Multi-term work function ($W_{\text{total}}$), latency, and memory traffic measured.
5. **SCORE & SELECT**: Top performers selected along non-dominated Pareto frontier.
6. **MUTATE & RECOMBINE**: Tile sizes, CPU/iGPU partition ratios, and approximation tolerances mutated.
7. **PERSIST**: Certified champions saved to persistent Strategy Database.
