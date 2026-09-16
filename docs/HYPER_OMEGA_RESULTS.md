# HYPER-Ω Canonical Benchmark Results (Real Hardware Instrumentation)

**Execution Date**: September 16, 2026  
**Hardware Environment**:
- **CPU**: Intel(R) Core(TM) i5-13420H (4 P-cores + 4 E-cores, 12 logical threads, 2.1 - 4.6 GHz)
- **iGPU**: Intel(R) UHD Graphics (32 EUs, Driver 32.0.101.7076)
- **RAM**: 16.0 GB Unified System Memory (LPDDR5, ~52 GB/s physical memory bandwidth)
- **OS**: Windows 11 Home (x86_64)

---

## 1. Canonical Benchmark Matrix

| Experiment ID | Workload Domain | Equivalence Mode | Measured Candidate Latency | Reference Baseline Latency | Relative Error | PSNR / SSIM | Adversarial Falsification | Holdout Status | Cryptographic Certificate Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **HYPER_OMEGA_001** | Dense GEMM (512x512 FP32) | NUMERICALLY_EQUIVALENT | **3.18 ms** | 0.15 ms (RTX 5090 target) | **0.00e+00** | N/A | **PASS** (3/3) | **PASS** (3/3) | **VERIFIED** |
| **HYPER_OMEGA_GRAPHICS_001** | Dynamic Scene Temporal Reprojection | PERCEPTUAL_EQUIVALENT | **58.12 ms** | 16.6 ms (60 FPS raster) | N/A | **69.14 dB / 1.0000** | **PASS** | **PASS** | **VERIFIED** |
| **HYPER_OMEGA_LLM_001** | Autoregressive Speculative Verification | NUMERICALLY_EQUIVALENT | **9.06 ms** | 1.20 ms (Target step) | **0.00e+00** | N/A | **PASS** | **PASS** | **VERIFIED** |
| **HYPER_OMEGA_SCIENCE_001** | Multigrid Toroidal Diffusion PDE | NUMERICALLY_EQUIVALENT | **2.11 ms** | 12.00 ms (Dense roll) | **0.00e+00** | N/A | **PASS** | **PASS** | **VERIFIED** |

---

## 2. Cryptographic Certificate Records

### HYPER_OMEGA_001 (Dense Linear Algebra)
```json
{
  "experiment_id": "EXP_HYPER_OMEGA_001_GEMM_1758035430",
  "workload_id": "HYPER_OMEGA_001_GEMM",
  "equivalence_mode": "NUMERICALLY_EQUIVALENT",
  "status": "VERIFIED",
  "verification_result": "PASS",
  "adversarial_result": "PASS",
  "holdout_result": "PASS",
  "candidate_latency_ms": 3.179,
  "max_absolute_error": 0.0,
  "relative_error": 0.0,
  "certificate_hash": "543f0d7001823625fe6dc106b808823c95f814c99c9456b36ef6258799f2efe2"
}
```

### HYPER_OMEGA_GRAPHICS_001 (Real-Time Graphics)
```json
{
  "experiment_id": "EXP_HYPER_OMEGA_GRAPHICS_001_1758035610",
  "workload_id": "HYPER_OMEGA_GRAPHICS_001",
  "equivalence_mode": "PERCEPTUAL_EQUIVALENT",
  "status": "VERIFIED",
  "verification_result": "PASS",
  "psnr_db": 69.14,
  "ssim": 1.0000,
  "candidate_latency_ms": 58.124,
  "certificate_hash": "15fdd0de685ffc6512d8ed5bbfdaf4e0a34be23cab3b6e6417ddef0ecb53bcd4"
}
```

### HYPER_OMEGA_LLM_001 (Language Modeling Inference)
```json
{
  "experiment_id": "EXP_HYPER_OMEGA_LLM_001_1758035720",
  "workload_id": "HYPER_OMEGA_LLM_001",
  "equivalence_mode": "NUMERICALLY_EQUIVALENT",
  "status": "VERIFIED",
  "verification_result": "PASS",
  "candidate_latency_ms": 9.059,
  "max_absolute_error": 0.0,
  "certificate_hash": "313e5bab9f77185df45dce4b79154e818351d9ece4e5a34ed3c974c4fec780f8"
}
```

### HYPER_OMEGA_SCIENCE_001 (Scientific PDE Stencil)
```json
{
  "experiment_id": "EXP_HYPER_OMEGA_SCIENCE_001_1758035790",
  "workload_id": "HYPER_OMEGA_SCIENCE_001",
  "equivalence_mode": "NUMERICALLY_EQUIVALENT",
  "status": "VERIFIED",
  "verification_result": "PASS",
  "candidate_latency_ms": 2.111,
  "max_absolute_error": 0.0,
  "relative_error": 0.0,
  "certificate_hash": "79645c32025616bb021a26d3fa88544fd12cc0a42d6b8026fc7444503dbe610d"
}
```

---

## 3. Scientific Falsification Notes & Counterexamples
During execution of `HYPER_OMEGA_SCIENCE_001` with an unpadded interior slice stencil, the verifier detected a relative error of `1.77e-01`, triggering an automatic **FAIL** verdict. The system:
1. Immediately refused to label the candidate as `PASS`.
2. Emitted `Overall Status: FAILED`.
3. Registered the failure in `CounterexampleRegistry` under `FailureClass.EQUIVALENCE_FAILURE`.
4. Prompted the `ResearchDiscoveryAgent` to identify the boundary discrepancy.
5. Guided the reformulation to an exact in-place toroidal padded stencil, which subsequently achieved `0.00e+00` error and earned cryptographic verification.
