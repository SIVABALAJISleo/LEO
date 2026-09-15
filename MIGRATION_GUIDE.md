# MIGRATION GUIDE: FROM EXPERIMENTAL PROTOTYPES TO THE VERIFIED COMPUTATION-ELIMINATION RUNTIME

**Target Package:** `hyper` (v10.0.0)  
**Status:** Deprecating historical prototypes (`archive_engines/`, `HYPER_v6_BREAKTHROUGH/`, ad-hoc scripts) into the unified, verified architecture.  

---

## 1. Migration Summary

Historical prototypes across the repository frequently relied on synthetic benchmarks, static dictionaries, and simulated token calculations. All production, testing, and benchmarking code should migrate to the formal modules under `hyper`:

| Historical Module / Script | Authoritative Module (`hyper/`) | Migration Action |
| :--- | :--- | :--- |
| `scripts/verify_100_percent.py` | `hyper.parity` & `hyper.benchmark` | Use `compute_contract_parity` instead of simulated token multipliers. |
| `archive_engines/.../cache.py` | `hyper.cache.exact_cache.ExactCache` | Replace basic dict caching with cryptographic multi-state cache keys. |
| `archive_engines/.../verifier.py` | `hyper.verification.verifier.VerificationEngine` | Use unified numerical, Freivalds, perceptual, and retrieval verifiers. |
| `universal_compute_router/...` | `hyper.scheduler.heterogeneous_scheduler` | Replace heuristic routing with measured `select_optimal_backend()`. |
| `benchmarks/hardware_check.py` | `hyper.hardware` & `hyper.cli` | Replace static CPU strings with dynamic `get_hardware_profile()`. |
| `core_ai/contracts.py` | `hyper.contracts.contract.Contract` | Replace legacy contracts with strict dataclass and `validate_contract()`. |

---

## 2. Code Example: Migrating to Formal Contract Execution

### Legacy Pattern (Deprecated)
```python
# DEPRECATED: Hardcoded speedups and unverified claims
res = {
    "speedup": 18.2,
    "verified": True,
    "contract_parity_pct": 100.0
}
```

### Modern Verified Pattern (Authoritative)
```python
import numpy as np
from hyper.contracts.contract import Contract, validate_contract
from hyper.candidate import CandidateResult, PathClass
from hyper.verification.verifier import VerificationEngine
from hyper.parity import compute_contract_parity

# 1. Define formal contract
contract = Contract(
    name="DenseMatmulSLO",
    exact_required=False,
    max_abs_error=0.01,
    max_relative_error=0.01,
    max_rmse=0.005,
    min_psnr=None,
    min_ssim=None,
    min_accuracy=None,
    min_recall=None,
    max_latency_ms=10.0,
    min_throughput=None,
    max_memory_bytes=None,
    allow_cache=True,
    allow_prediction=False,
    allow_approximation=True,
    allow_perceptual_difference=False
)
validate_contract(contract)

# 2. Execute and verify
A = np.random.randn(64, 64).astype(np.float32)
B = np.random.randn(64, 64).astype(np.float32)
expected = A @ B
candidate = A.astype(np.float16).astype(np.float32) @ B.astype(np.float16).astype(np.float32)

ver = VerificationEngine.verify_numerical(candidate, expected)

# 3. Create CandidateResult with provenance
result = CandidateResult(
    value=candidate,
    path_class=PathClass.NUMERICALLY_APPROXIMATE.value,
    backend="CPU_AVX2",
    latency_ms=0.25,
    work_units=64 * 64 * 64,
    memory_bytes=candidate.nbytes,
    max_abs_error=ver["max_abs_error"],
    relative_error=ver["relative_error"],
    rmse=ver["rmse"],
    provenance={"measurement_source": "local_execution", "synthetic": False}
)

# 4. Evaluate parity
parity = compute_contract_parity(contract, result)
print(f"Contract Passed: {parity['passed']} (Parity: {parity['parity_pct']}%)")
```
