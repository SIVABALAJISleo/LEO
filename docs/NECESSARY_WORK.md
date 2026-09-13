# HYPER / LEO — Necessary Work Specification & Accounting
**Document Version:** 2.0.0 (Ultra-Sonic Master Engineering)

---

## 1. Formal Arithmetic Accounting Ledger

Every workload executed within the HYPER pipeline formally accounts for operations across 10 distinct categories:

1. **`ORIGINAL_WORK`**: Baseline brute-force theoretical FLOPs.
2. **`NECESSARY_WORK`**: Minimum arithmetic FLOPs required to satisfy the observable contract.
3. **`ELIMINABLE_WORK`**: Total FLOPs rendered mathematically unnecessary ($W_{\text{original}} - W_{\text{necessary}}$).
4. **`REUSED_WORK`**: FLOPs eliminated through exact cryptographic caching ($W_{\text{reused}} = W_{\text{original}}$).
5. **`REFORMULATED_WORK`**: FLOPs executed under an algebraically transformed representation (e.g. Low-Rank, FFT).
6. **`APPROXIMATED_WORK`**: FLOPs computed under bounded numerical relaxation.
7. **`PREDICTED_WORK`**: FLOPs generated speculatively and subsequently accepted.
8. **`RECONSTRUCTED_WORK`**: FLOPs synthesized through spatial/temporal reprojection.
9. **`VERIFICATION_WORK`**: Independent sub-linear audit cost (e.g. Freivalds check).
10. **`FALLBACK_WORK`**: FLOPs executed if shortcut candidates fail verification.

---

## 2. Work Elimination Formula

$$\text{WORK\_ELIMINATION} = 1 - \frac{\text{NECESSARY\_WORK} + \text{VERIFICATION\_WORK}}{\text{ORIGINAL\_WORK}}$$

No number in this ledger is fabricated or hardcoded. Every entry is logged to `evidence_ledger.json` and signed in `execution_certificate.json`.
