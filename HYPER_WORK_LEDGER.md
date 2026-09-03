# HYPER: Computational Work Ledger & VWA Accounting

## 1. Zero Double-Counting Guarantee
The **Computational Work Ledger** enforces strict arithmetic conservation:
$$\text{Reference FLOPs} = \text{Eliminated FLOPs} + \text{Transformed Executed FLOPs}$$

No FLOP is counted as both eliminated and executed. Latency reductions resulting purely from memory bandwidth improvements or hardware clock boosts are never falsely conflated with algorithmic work avoidance.

---

## 2. Verified Work Avoidance (VWA) Metric
$$\text{VWA} = \frac{\text{Reference Required Work} - \text{Verified Actual Work}}{\text{Reference Required Work}} = 1 - \frac{W_{\text{actual}}}{W_{\text{baseline}}}$$

A non-zero VWA is recorded if and only if the resulting output passes independent verification against the frozen contract.

---

## 3. Ledger Entry Schema
```json
{
  "timestamp": "2026-09-03T07:15:00Z",
  "workload_name": "dense_gemm_fp32",
  "reference_flops": 2147483648,
  "executed_flops": 536870912,
  "eliminated_flops": 1610612736,
  "transformed_flops": 536870912,
  "verified_work_avoidance": 0.7500,
  "verification_passed": true,
  "verifier_method": "FreivaldsRandomizedCheck"
}
```
Entries are automatically written to `HYPER_3_0_WORK_LEDGER.json`.
