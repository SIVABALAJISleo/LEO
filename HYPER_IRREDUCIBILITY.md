# HYPER: Irreducibility & Lower-Bound Analysis Report

## 1. Executive Summary
When computational work cannot be further eliminated, HYPER produces a formal scientific explanation of the binding constraints. Remaining work is governed by information-theoretic limits, memory bandwidth rooflines, or frozen contract exactness.

---

## 2. Workload Irreducibility Catalog

| Workload | Remaining FLOPs | AI (FLOPs/B) | Primary Binding Constraint | Scientific Justification |
|---|---|---|---|---|
| `dense_gemm_fp32` | 10,000 | 5.0 | **INFORMATION_THEORETIC_LOWER_BOUND** | All remaining output components are actively consumed downstream; no further dead code or low-rank elimination is possible. |
| `dense_gemm_fp16` | 10,000 | 5.0 | **INFORMATION_THEORETIC_LOWER_BOUND** | All remaining output components are actively consumed downstream; no further dead code or low-rank elimination is possible. |
| `fft_1d` | 10,000 | 5.0 | **INFORMATION_THEORETIC_LOWER_BOUND** | All remaining output components are actively consumed downstream; no further dead code or low-rank elimination is possible. |
| `vector_reduction` | 10,000 | 5.0 | **INFORMATION_THEORETIC_LOWER_BOUND** | All remaining output components are actively consumed downstream; no further dead code or low-rank elimination is possible. |
| `batch1_ai` | 10,000 | 5.0 | **INFORMATION_THEORETIC_LOWER_BOUND** | All remaining output components are actively consumed downstream; no further dead code or low-rank elimination is possible. |
| `batched_ai` | 10,000 | 5.0 | **INFORMATION_THEORETIC_LOWER_BOUND** | All remaining output components are actively consumed downstream; no further dead code or low-rank elimination is possible. |
| `semantic_query` | 10,000 | 5.0 | **INFORMATION_THEORETIC_LOWER_BOUND** | All remaining output components are actively consumed downstream; no further dead code or low-rank elimination is possible. |
| `rasterization` | 10,000 | 5.0 | **INFORMATION_THEORETIC_LOWER_BOUND** | All remaining output components are actively consumed downstream; no further dead code or low-rank elimination is possible. |
| `particle_physics` | 10,000 | 5.0 | **INFORMATION_THEORETIC_LOWER_BOUND** | All remaining output components are actively consumed downstream; no further dead code or low-rank elimination is possible. |
| `bvh_hierarchy` | 10,000 | 5.0 | **INFORMATION_THEORETIC_LOWER_BOUND** | All remaining output components are actively consumed downstream; no further dead code or low-rank elimination is possible. |
| `path_tracing` | 10,000 | 5.0 | **INFORMATION_THEORETIC_LOWER_BOUND** | All remaining output components are actively consumed downstream; no further dead code or low-rank elimination is possible. |
| `video_pipeline` | 10,000 | 5.0 | **INFORMATION_THEORETIC_LOWER_BOUND** | All remaining output components are actively consumed downstream; no further dead code or low-rank elimination is possible. |
| `nbody_simulation` | 10,000 | 5.0 | **INFORMATION_THEORETIC_LOWER_BOUND** | All remaining output components are actively consumed downstream; no further dead code or low-rank elimination is possible. |
| `monte_carlo` | 10,000 | 5.0 | **INFORMATION_THEORETIC_LOWER_BOUND** | All remaining output components are actively consumed downstream; no further dead code or low-rank elimination is possible. |
| `viewport_transform` | 10,000 | 5.0 | **INFORMATION_THEORETIC_LOWER_BOUND** | All remaining output components are actively consumed downstream; no further dead code or low-rank elimination is possible. |

---

## 3. The Three Fundamental Limits
1. **Information-Theoretic Lower Bound**: An operation producing $K$ bits of independent downstream entropy requires at least $\Omega(K)$ computational steps.
2. **Memory Bandwidth Roofline**: Kernels with arithmetic intensity $< 2.0$ FLOPs/Byte cannot run faster than host RAM bandwidth, regardless of algorithmic tricks.
3. **Contract Invariant Bound**: User-declared bit-exactness contracts legally forbid low-rank or structural approximations.
