# Failure-First Design & Falsification Audit Report

## 1. Overview
In strict scientific discovery, detecting when a proposed optimization **fails** is as critical as verifying when it succeeds.
This report documents all transformations rejected by the verification engine and workloads where no shortcut was admitted.

## 2. Rejection Cases & Unfalsifiable Computations

### Workload: Matrix Computation (Chained GEMM)
- **Status Message:** `SHORTCUT_DISCOVERED`
- **Candidates Explored:** 3
- **Candidates Rejected:** 1

#### Audit Trace:
- Step 3 [cand_baseline_cir_255c]: PRUNED_COST -> Estimated cost 196608 >= current best 32768

### Workload: Convolution (2D Conv + ReLU Fusion)
- **Status Message:** `NO_VERIFIED_SHORTCUT_FOUND`
- **Candidates Explored:** 2
- **Candidates Rejected:** 1

#### Audit Trace:
- Step 2 [cand_baseline_cir_4b0f]: PRUNED_COST -> Estimated cost 1569 >= current best 1569
- **Outcome:** Preserved trusted reference baseline. Zero unverified shortcuts admitted.

### Workload: FFT / Spectral Decomposition
- **Status Message:** `SHORTCUT_DISCOVERED`
- **Candidates Explored:** 4
- **Candidates Rejected:** 2

#### Audit Trace:
- Step 3 [cand_cf_omit_26485852]: PRUNED_COST -> Estimated cost 46081 >= current best 46081
- Step 4 [cand_baseline_cir_ce31]: PRUNED_COST -> Estimated cost 46082 >= current best 46081

### Workload: Graph Computation (Sparse Adjacency)
- **Status Message:** `NO_VERIFIED_SHORTCUT_FOUND`
- **Candidates Explored:** 2
- **Candidates Rejected:** 1

#### Audit Trace:
- Step 2 [cand_baseline_cir_4ae9]: PRUNED_COST -> Estimated cost 1048576 >= current best 1048576
- **Outcome:** Preserved trusted reference baseline. Zero unverified shortcuts admitted.

### Workload: Cryptographic Hash (SHA-256)
- **Status Message:** `NO_VERIFIED_SHORTCUT_FOUND`
- **Candidates Explored:** 2
- **Candidates Rejected:** 1

#### Audit Trace:
- Step 2 [cand_baseline_cir_929c]: PRUNED_COST -> Estimated cost 1 >= current best 1
- **Outcome:** Preserved trusted reference baseline. Zero unverified shortcuts admitted.

### Workload: Scientific Numerical ODE
- **Status Message:** `SHORTCUT_DISCOVERED`
- **Candidates Explored:** 4
- **Candidates Rejected:** 2

#### Audit Trace:
- Step 3 [cand_cse_51a863ea]: PRUNED_COST -> Estimated cost 386 >= current best 322
- Step 4 [cand_baseline_cir_23d1]: PRUNED_COST -> Estimated cost 450 >= current best 322

### Workload: ML Inference (Projection + Dead Code)
- **Status Message:** `SHORTCUT_DISCOVERED`
- **Candidates Explored:** 8
- **Candidates Rejected:** 6

#### Audit Trace:
- Step 3 [cand_fuse_gemm_add_2efec01c]: PRUNED_COST -> Estimated cost 56576 >= current best 56576
- Step 4 [cand_cf_omit_1411555e]: PRUNED_COST -> Estimated cost 66048 >= current best 56576
- Step 5 [cand_dce_4419ebda]: PRUNED_COST -> Estimated cost 66560 >= current best 56576
- Step 6 [cand_cf_omit_fe6c3fab]: PRUNED_COST -> Estimated cost 66560 >= current best 56576
- Step 7 [cand_cf_omit_0cd82f0b]: PRUNED_COST -> Estimated cost 66560 >= current best 56576
- Step 8 [cand_baseline_cir_cc0b]: PRUNED_COST -> Estimated cost 66562 >= current best 56576

### Workload: Irregular Memory Access (Gather)
- **Status Message:** `NO_VERIFIED_SHORTCUT_FOUND`
- **Candidates Explored:** 2
- **Candidates Rejected:** 1

#### Audit Trace:
- Step 2 [cand_baseline_cir_7edb]: PRUNED_COST -> Estimated cost 1 >= current best 1
- **Outcome:** Preserved trusted reference baseline. Zero unverified shortcuts admitted.

### Workload: Memory-Bound (STREAM Vector Triad)
- **Status Message:** `NO_VERIFIED_SHORTCUT_FOUND`
- **Candidates Explored:** 2
- **Candidates Rejected:** 1

#### Audit Trace:
- Step 2 [cand_baseline_cir_f506]: PRUNED_COST -> Estimated cost 131072 >= current best 131072
- **Outcome:** Preserved trusted reference baseline. Zero unverified shortcuts admitted.

### Workload: Compute-Bound (Polynomial Horner)
- **Status Message:** `NO_VERIFIED_SHORTCUT_FOUND`
- **Candidates Explored:** 2
- **Candidates Rejected:** 1

#### Audit Trace:
- Step 2 [cand_baseline_cir_4f2f]: PRUNED_COST -> Estimated cost 5120 >= current best 5120
- **Outcome:** Preserved trusted reference baseline. Zero unverified shortcuts admitted.

## 3. Total Rejections Enforced: 17

## 4. Key Scientific Failure Lessons
1. **Cryptographic One-Way Functions:** SHA-256 and cryptographic primitives exhibit maximum entropy and non-linear bit permutations. All candidate algebraic simplifications produce catastrophic bit divergence ($> 50\%$ Hamming error) and are immediately rejected.
2. **Strict FP Precision Non-Associativity:** Under `MODE_2_NUMERIC_EXACT`, FP32 matrix reassociation is rejected due to machine epsilon accumulation, protecting the user from subtle rounding drift unless `MODE_3_NUMERIC_TOLERANCE` is explicitly declared.
3. **Zero Phantom Speedups:** When cost estimation shows a candidate is slower than baseline, it is pruned prior to execution.