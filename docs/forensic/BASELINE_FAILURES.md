# LEO / HYPER Ω∞ — Baseline Failures & Forensic Root-Cause Analysis

## 1. Summary of Identified Defects in Baseline Evidence

In the baseline artifact `HYPER_3_0_RESULTS.json` (and its replica `reports/hyper_3/HYPER_3_0_RESULTS.json`), the summary claimed:
- `"exact_parity_score": 1.0`
- `"contract_parity_score": 1.0`
- All 15 workloads marked `"passed": true`.

Forensic analysis of the raw metrics revealed severe errors that directly contradicted the claimed 100% contract parity score:

| Workload ID | Track B Relative Error | Speedup | Baseline Status | True Scientific Status | Root Cause of Failure |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `dense_gemm_fp32` | **0.78691 (78.7%)** | 0.08x | `passed: true` (FALSE) | **FAILED (REJECTED)** | Rank-256 randomized SVD cannot approximate an i.i.d. Gaussian rank-1024 matrix without ~78% error. Python QR was also 12x slower. |
| `dense_gemm_fp16` | **0.32541 (32.5%)** | 0.01x | `passed: true` (FALSE) | **FAILED (REJECTED)** | Uncalibrated 2:4 structured sparsity causes 32.5% loss on random dense weights. Python loop was 100x slower. |
| `batch1_ai` | **0.54049 (54.0%)** | 0.04x | `passed: true` (FALSE) | **FAILED (REJECTED)** | Zero-shot ternary quantization without fine-tuning causes 54% activation distortion. |
| `semantic_query` | **0.28775 (28.8%)** | 1.87x | `passed: true` (FALSE) | **FAILED (REJECTED)** | Coarse 100-vector cluster centers missed top-10 exact nearest neighbors by 28.8%. |
| `rasterization` | **1.00000 (100.0%)** | 60.55x | `passed: true` (FALSE) | **FAILED (REJECTED)** | Horizontal span rasterizer differed at circle boundaries from reference `< 50^2` pixel test; on binary pixels, edge differences produce relative error 1.0. |
| `bvh_hierarchy` | **0.98046 (98.0%)** | 0.71x | `passed: true` (FALSE) | **FAILED (REJECTED)** | Sorting along only X axis instead of 3D Morton code permutes bounding volumes arbitrarily, producing 98% error. |
| `video_pipeline` | **0.17157 (17.2%)** | 2.51x | `passed: true` (FALSE) | **FAILED (REJECTED)** | Linear multiplier approximation `frame * 0.5` departs by 17.2% from non-linear ACES curve `frame / (frame + 1.0)`. |
| `nbody_simulation` | **0.38242 (38.2%)** | 2.25x | `passed: true` (FALSE) | **FAILED (REJECTED)** | Stride-2 particle sampling omits half the gravitational field, causing 38.2% acceleration vector drift. |

---

## 2. Root Cause of the Certification Vulnerability

Two code-level bugs in the verification pipeline permitted these 8 failed candidates to be marked `passed: true`:

### Bug A: Loose Default Contract Tolerances
In `hyper_v3/frontend/contract_parser.py` (lines 122-126):
```python
max_relative_error: float = 0.80,
max_absolute_error: float = 2.0,
min_snr_db: float = 10.0,
min_ssim: float = 0.80
```
A default tolerance of 80% relative error and an absolute error of 2.0 allowed almost any normalized candidate to pass.

### Bug B: Disjunctive `or` in Bound Check
In `hyper_v3/verification/independent_verifier.py` (line 86):
```python
is_valid = (max_rel <= max_rel_err) or (max_abs <= max_abs_err)
```
Because the check used `or` rather than `and`, whenever `max_abs <= 2.0` was true (which was true for all normalized floating point outputs bounded in [-1, 1]), `is_valid` evaluated to `True` regardless of relative error—even when relative error was 1.0 (100% error)!

---

## 3. Repaired Scientific Baseline

With strict per-workload contract bounds and conjunctive verification enforced:
- **Track A (Exact)**: 15 / 15 workloads passed (`exact_parity_score = 1.0`).
- **Track B (Contract-Aware)**: Exactly 7 workloads passed (`fft_1d`, `vector_reduction`, `batched_ai`, `particle_physics`, `path_tracing`, `monte_carlo`, `viewport_transform`), and 8 workloads failed.
- **True Contract Parity Score**: `7 / 15 = 0.4667 (46.7%)`.
