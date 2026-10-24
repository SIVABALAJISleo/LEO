# HYPER Computational Phase-Change Engine (CPCE) — Baseline Tests & Environment Audit

**Audit Date**: October 2026  
**Host Target**: Lenovo IdeaPad Slim 3 15IAH8 (Intel Core i5-13420H, 16 GB RAM, Windows 11 Home)  
**Python Runtime**: 3.13.5  
**Node.js**: v22.12.0

---

## 1. Verified Baseline Test Runs

Prior to implementing the CPCE package, authoritative regression test runs were executed across the platform:

### Suite 1: Benchmark Provenance & Guard Test Suite

- **Command**: `python -m pytest tests/test_benchmark_provenance_truth.py -v`
- **Collected**: 6 tests
- **Results**: `6 passed in 8.30s` (Exit code: 0)
- **Verified Invariants**:
  1. `test_reference_engine_provenance_and_no_fake_hardware`: PASS. Local host baseline correctly tagged `MEASURED`; simulated targets tagged `SIMULATED_REFERENCE`.
  2. `test_omega_runner_no_latency_ratio_work_elimination`: PASS. Dense GEMM reports 0.0% work elimination under honest operational FLOP model.
  3. `test_omega_runner_fail_closed_on_adversarial_failure`: PASS. Status fails closed to `FAILED` upon adversarial gauntlet failure.
  4. `test_omega_runner_fail_closed_on_holdout_failure`: PASS. Status fails closed to `FAILED` upon holdout gauntlet failure.
  5. `test_opencl_uva_truthful_copy_reporting`: PASS. Truthfully reports `copy_overhead_bytes > 0` and `is_zero_copy: False`.
  6. `test_heterogeneous_orchestrator_truthful_fallback`: PASS. Reports `CPU_ONLY_FALLBACK` when GPU is absent.

### Suite 2: Real Local AI Inference Suite

- **Command**: `python -m pytest tests/test_local_inference_product.py -v`
- **Collected**: 3 tests
- **Results**: `3 passed in 89.18s` (Exit code: 0)
- **Verified Invariants**:
  1. `test_inference_model_info`: PASS. GGUF model `Qwen2.5-0.5B-Instruct-Q4_K_M` (491 MB) discovered, local-only verified.
  2. `test_inference_real_generation`: PASS. Tokens generated on local CPU with measured TTFT and token throughput.
  3. `test_inference_benchmark_endpoint`: PASS. Multi-trial benchmark computes median TTFT and throughput with zero network dependency.

### Suite 3: Canonical Dense GEMM Benchmark

- **Command**: `python benchmarks/hyper_omega_001_gemm.py`
- **Output**: Verified reference latency 1.710 ms, candidate latency 2.007 ms, measured speedup 0.85x, candidate RAM 1.50 MB, status `VERIFIED`.

### Suite 4: Frontend Production Build

- **Command**: `npm run build`
- **Result**: Nitro + Vite production bundle compiled in `2.99s` with zero errors.
