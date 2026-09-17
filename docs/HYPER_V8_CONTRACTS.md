# HYPER v8 Contract Specification

## 1. Principle of Explicit Application Contracts

In HYPER v8, **no optimization runs without an explicit contract**. 
An optimization that produces incorrect results, even if 1000x faster, has a value of negative infinity.

### Contract Types

1. **Exact Contract (`exact_contract`)**:
   - `correctness_mode`: `"EXACT"`
   - `abs_error_max`: $0.0$
   - `approximation_allowed`: `False`
   - `caching_allowed`: `True`
   - `strict_100_mode`: `True`
   - Intended for: Financial ledgering, cryptographic kernels, scientific simulation steps where accumulation error is fatal.

2. **Numerical Contract (`numerical_contract`)**:
   - `correctness_mode`: `"NUMERICAL"`
   - `abs_error_max`: Bounded tolerance (e.g. $10^{-6}$ or $10^{-2}$)
   - `rel_error_max`: Bounded relative tolerance
   - `approximation_allowed`: `True`
   - Intended for: Machine learning inference, approximate matrix factorizations, iterative solvers.

3. **Real-Time Contract (`realtime_contract`)**:
   - `correctness_mode`: `"NUMERICAL"`
   - `latency_max_ms`: Strict latency ceiling (e.g. $16.66$ ms for 60 FPS)
   - `fps_min`: Target frame rate
   - `prediction_allowed`: `True`
   - Intended for: Interactive rendering, robotics telemetry, streaming audio/video.

---

## 2. Execution Provenance & Certificates

Every result produced by HYPER v8 carries an immutable `ExecutionCertificate`:
```json
{
  "path_type": "EXACT_RESIDUAL",
  "verification_status": "VERIFIED_EXACT",
  "input_digest": "4f9d2a1b...",
  "output_digest": "8c3e109a...",
  "device": "Intel Core i5-12450H",
  "algorithm": "exact_residual_row_delta",
  "max_abs_error": "0.000e+00",
  "max_rel_error": "0.000e+00",
  "reference_time_ms": 0.3983,
  "execution_time_ms": 0.0675,
  "verification_time_ms": 0.0012,
  "total_time_ms": 0.0687,
  "speedup": 5.9,
  "contract_name": "exact_256",
  "contract_passed": true,
  "fallback_used": false
}
```

If the candidate result exceeds the contract's tolerance or misses a latency deadline, the `ContractValidator` automatically rejects the candidate and triggers the verified `FALLBACK` path.
