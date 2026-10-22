# HYPER Computational Phase-Change Engine (CPCE) — Known Defects & Remediation Log

**Audit Date**: October 2026  
**Status**: Authoritative Forensic Log  
**Auditor**: Principal Architecture & Verification Engineer  

---

## 1. Catalog of Audited & Remediated Defects

| Defect ID | Severity | File Location | Original Defective Behavior | Remediated Status | Verification Test |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `DEF-001` | **CRITICAL (P0)** | `benchmarks/hyper_omega_001_gemm.py` | Passed `reference_latency_ms=0.15` as a simulated RTX 5090 timing. | **RESOLVED**. Evaluates local measured baseline (`np.matmul`), outputs honest speedup, marks discrete GPU comparison as `UNKNOWN`. | `benchmarks/hyper_omega_001_gemm.py` |
| `DEF-002` | **CRITICAL (P0)** | `hyper_x/omega_runner.py` | Derived candidate FLOPs from execution latency ratio (`cand_lat / ref_lat`). | **RESOLVED**. Operation counts derive strictly from declared mathematical operation models. | `tests/test_benchmark_provenance_truth.py::test_omega_runner_no_latency_ratio_work_elimination` |
| `DEF-003` | **CRITICAL (P0)** | `hyper_x/omega_runner.py` | Candidate memory calculated as `nominal * 0.7` without measurement; iGPU time fixed to `0.0`. | **RESOLVED**. Measures real memory via `tracemalloc` and tensor `nbytes`. | `benchmarks/hyper_omega_001_gemm.py` |
| `DEF-004` | **CRITICAL (P0)** | `hyper_x/omega_runner.py` | Certification bypass: marked status `VERIFIED` even when adversarial or holdout tests failed. | **RESOLVED**. Enforced 100% fail-closed gate: failure in any gauntlet returns `FAILED`. | `tests/test_benchmark_provenance_truth.py::test_omega_runner_fail_closed_on_adversarial_failure` |
| `DEF-005` | **CRITICAL (P0)** | `hyper/extreme/opencl_uva.py` | Reported `copy_overhead_bytes: 0` and `is_zero_copy: True` despite copying data with `ctypes.memmove`. | **RESOLVED**. Reports true copied bytes (`3 * nbytes`), labeled `HOST_PINNED_MAPPED_COPY` with `is_zero_copy = False`. | `tests/test_benchmark_provenance_truth.py::test_opencl_uva_truthful_copy_reporting` |
| `DEF-006` | **HIGH (P1)** | `hyper_x/reference_engine.py` | Hardcoded `gpu_identity="NVIDIA GeForce RTX 5090..."` without checking physical presence. | **RESOLVED**. Requires explicit `provenance="SIMULATED_REFERENCE"` or uses host baseline. | `tests/test_benchmark_provenance_truth.py::test_reference_engine_provenance_and_no_fake_hardware` |
| `DEF-007` | **HIGH (P1)** | `hyper_x/heterogeneous_orchestrator.py` | Returned `execution_mode="HETEROGENEOUS_CPU_IGPU_HYBRID"` even when GPU fallback was triggered. | **RESOLVED**. Truthfully reports `CPU_ONLY_FALLBACK` and runs concurrent threads when GPU is available. | `tests/test_benchmark_provenance_truth.py::test_heterogeneous_orchestrator_truthful_fallback` |

---

## 2. Active Technical Boundaries for CPCE

1. **Memory Bandwidth Ceiling**: Host laptop uses dual-channel DDR system RAM with peak throughput of 38–68 GB/s. Unstructured streaming operations cannot match 1,000+ GB/s HBM bandwidth through software alone.
2. **Computational Irreducibility**: Random unstructured full-rank dense matrices cannot have arithmetic operations eliminated without violating IEEE 754 precision contracts.
3. **Approximation Boundary**: A quality contract relaxation (e.g. perceptual reconstruction or INT4 quantization) is strictly categorized as `APPROXIMATE`, never mislabeled as bitwise exact compute.
