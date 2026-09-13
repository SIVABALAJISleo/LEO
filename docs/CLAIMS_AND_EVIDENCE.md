# HYPER / LEO Claims and Evidence Ledger

## 1. Verified Claims Matrix
Every claim in the project is mapped to an authoritative source file, a physical test script, and an evidence artifact:

| Claim | Status | Supporting Code | Evidence Artifact |
| :--- | :--- | :--- | :--- |
| **Sub-100µs Heterogeneous Dispatch** | **VERIFIED** | `universal_compute_router/adaptive_dispatch.py` | Mean: 0.75 µs, P99: 3.60 µs (`tests/test_performance_regression.py`) |
| **INT4 8x Parameter Compression** | **VERIFIED** | `benchmarks/benchmark_int4_vs_fp32.py` | `int4_vs_fp32_benchmark.json` (60.9 MB model RAM vs ~490 MB FP32) |
| **Interactive LLM on Target Silicon** | **VERIFIED** | `leo_implementation_artifacts.py` | `week1_baseline.json` (TTFT: 417 ms, 27.2 tok/s on i5-12450H) |
| **25% Token Merging with 0 Drift** | **VERIFIED** | `hyper_runtime/token_merging/tome_engine.py` | Weighted cosine similarity = 1.0000, 3.17 ms latency |
| **Block-Sparse Attention 2.9x Speedup**| **VERIFIED** | `hyper_runtime/sparse_attention.py` | 27.76 ms (Dense) -> 9.56 ms (Sparse) at N=1024, 93.75% sparsity |
| **Semantic Boilerplate Pruning (50%)** | **VERIFIED** | `hyper_runtime/semantic_token_pruning.py` | 100 tokens -> 50 tokens in 0.40 ms (`tests/test_integration_prompts.py`) |
| **Freivalds Honest Fallback on Noise** | **VERIFIED** | `ace_engine.py` | `falsification.json` (Gaussian white noise correctly falls back to exact) |
| **Raw Hardware Throughput Parity** | **DISPROVEN / UNPROVEN** | `None` | Physical FLOPs parity with RTX 4090 silicon is impossible on 45W package |

---

## 2. Evidence Classification Summary
1. All positive performance claims must be backed by real timestamps from physical host silicon.
2. Negative results (e.g. white noise cannot be compressed, unverified draft models drift) are published as proof of scientific honesty.
