# HYPER: Proof & Exactness Certificate Specification

## 1. Zero Self-Certification Rule
In HYPER, the component that generates an optimization is strictly prohibited from certifying its own correctness.
Every candidate transformation must be formally proven or independently verified by segregated verification kernels.

---

## 2. Certificate Taxonomy & SHA-256 Hashes
Every execution produces a cryptographically signed `ExactnessCertificate`:

```json
{
  "certificate_id": "cert_d78f1a...",
  "workload_name": "dense_gemm_fp32",
  "equivalence_type": "NUMERICALLY_BOUNDED",
  "max_relative_error": 0.0412,
  "allowed_error": 0.0500,
  "verification_method": "FreivaldsRandomizedCheck",
  "independent_verification": true,
  "contract_satisfied": true
}
```

### Equivalence Classes:
- `EXACT`: Bitwise identical output ($E_{\text{rel}} == 0$).
- `FORMALLY_EQUIVALENT`: Exact under associative/distributive real arithmetic.
- `NUMERICALLY_BOUNDED`: Error strictly bounded by contract $\|y - \hat{y}\| \le \varepsilon$.
- `PERCEPTUALLY_BOUNDED`: Visual or auditory similarity metric satisfies threshold ($\text{SSIM} \ge 0.95$).
- `STATISTICALLY_BOUNDED`: Distributional convergence within confidence interval.
- `UNVERIFIED`: Optimization rejected; immediate fallback to reference gold standard.
