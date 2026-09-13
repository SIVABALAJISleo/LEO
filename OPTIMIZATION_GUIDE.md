# LEO / HYPER: Verified Optimization & Parity Guide

## Target Hardware Profile
- **Processor**: 12th Gen Intel(R) Core(TM) i5-12450H (Alder Lake Architecture)
- **Cores / Threads**: 8 Physical Cores (4 Golden Cove P-cores, 4 Gracemont E-cores) / 12 Logical Threads
- **iGPU**: Intel(R) UHD Graphics (48 Execution Units, 1.20 GHz max frequency)
- **Vector Instruction Sets**: AVX2, FMA3, OpenVINO / oneDNN acceleration
- **Thermal Envelope**: 45W Shared Package TDP
- **Host Memory**: 16 GB Unified System RAM

---

## Architecture Overview

```
                          [ Input Sequence / Query ]
                                      │
                         ┌────────────▼────────────┐
                         │   Phase C1: TokenPruner │ (Eliminates 30-50% redundant boilerplate)
                         └────────────┬────────────┘
                                      │
                         ┌────────────▼────────────┐
                         │   Phase B3: ToMe Engine │ (Bipartite matching, 25% reduction, <3% drift)
                         └────────────┬────────────┘
                                      │
                         ┌────────────▼────────────┐
                         │   Phase B1: Router      │ (< 10µs dispatch: P-core vs E-core vs iGPU)
                         └────────────┬────────────┘
                                      │
         ┌────────────────────────────┼────────────────────────────┐
         ▼                            ▼                            ▼
  [ Softmax / Reductions ]    [ Attention (N > 2048) ]      [ Linear Projections ]
     CPU P-core (AVX2)         iGPU (48 EU) or Sparse        INT4 Quantized (8x compression)
                               (Phase C2: O(N log N))        (Phase B2 / C3: SVD-Adaptive)
```

---

## Optimization Matrix & How to Toggle

| Phase | Component | Location | Default Config | How to Toggle / Tune |
| :--- | :--- | :--- | :--- | :--- |
| **B1** | **Adaptive Dispatch Router** | `universal_compute_router/adaptive_dispatch.py` | Sub-100µs heuristic rule set | Pass `has_igpu=True/False` to toggle iGPU offload. |
| **B2** | **INT4 Quantized Inference** | `benchmarks/benchmark_int4_vs_fp32.py` | Q4_K_M GGUF format (8x RAM reduction) | Load GGUF via `llama-cpp-python` or switch precision. |
| **B3** | **Token Merging (ToMe)** | `hyper_runtime/token_merging/tome_engine.py` | `merge_ratio=0.25`, `min_similarity=0.80` | Tune `merge_ratio` from `0.10` to `0.50` in runtime configs. |
| **B4** | **Speculative Decoding** | `hyper_runtime/speculative_decoding/` | $K=4$, $\alpha \ge 0.70$ | Adjust draft token count $K \in [2, 4, 6]$ via `SpeculativeExecutionEngine`. |
| **C1** | **Semantic Token Pruning** | `hyper_runtime/semantic_token_pruning.py` | `similarity_threshold=0.88`, `min_preserve=0.50` | Enable before Layer 0 embedding forward pass. |
| **C2** | **Block-Sparse Attention** | `hyper_runtime/sparse_attention.py` | Local window $w=32$, stride $=16$ | Engaged automatically when $N \ge 1024$ (up to 2.9x speedup). |
| **C3** | **SVD-Adaptive Precision** | `hyper_runtime/adaptive_precision.py` | $\kappa_{\text{eff}} < 25 \rightarrow \text{INT4}$, $\kappa_{\text{eff}} < 100 \rightarrow \text{INT8}$ | Run `AdaptivePrecisionSelector.analyze_matrix(W)`. |

---

## Measured Hardware Benchmarks (Intel Core i5-12450H)

All metrics below are measured wall-clock measurements from host silicon:

### 1. Real Model Latency & Memory (`week1_baseline.json`)
- **Model**: `Qwen2.5-0.5B-Instruct-Q4_K_M.gguf`
- **Time to First Token (TTFT)**: **417.62 ms** (Target: $< 1000$ ms) ✅
- **256-Token Generation**: **9.41 s** (Target: $< 30$ s, 27.19 tok/s) ✅
- **Process Memory (RSS)**: **477.61 MB** (vs ~3.8 GB for full FP32) ✅

### 2. Dispatch Latency (`universal_compute_router/adaptive_dispatch.py`)
- **Mean Decision Latency**: **0.75 µs** (Target: $< 100$ µs) ✅
- **P99 Decision Latency**: **3.60 µs** ✅
- **Dispatch Policy**: Softmax strictly pinned to CPU P-cores; attention $> 2048$ tokens routed to iGPU.

### 3. Sequence Compression & Drift (`hyper_runtime/token_merging/`)
- **Tokens Reduced**: 25.0% reduction on 128-token activation sequences.
- **Representation Drift**: Cosine similarity $= 1.000$ (proportional token weighting), drift $< 0.001$.
- **Latency Overhead**: 3.17 ms per 128-token chunk.

### 4. Attention Scaling (`hyper_runtime/sparse_attention.py`)
- **$N = 1024$**: 27.76 ms (Dense) $\rightarrow$ **9.56 ms (Sparse)** (**2.90x Speedup**, 93.75% Sparsity) ✅
- **$N = 2048$**: 97.66 ms (Dense) $\rightarrow$ **41.46 ms (Sparse)** (**2.36x Speedup**, 93.75% Sparsity) ✅

---

## Running Verification & Regression Tests

```bash
# Run unit & regression test suite (< 1 minute)
python -m pytest tests/test_performance_regression.py -v
python -m pytest tests/test_integration_prompts.py -v
python -m pytest tests/test_pathological_inputs.py -v

# Run real hardware benchmark
python leo_implementation_artifacts.py --mode benchmark --output week1_baseline.json

# Run adversarial falsification suite
python leo_implementation_artifacts.py --mode falsify --output falsification.json
```
