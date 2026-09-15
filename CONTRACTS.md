# LEO/HYPER FORMAL CONTRACT SPECIFICATION

**Module Reference:** `hyper.contracts.contract`  
**Schema Version:** 10.0.0  

---

## 1. Overview

In LEO/HYPER, no computation is skipped, approximated, or altered without an explicit, validated **Application Contract**. The contract defines the mathematical, perceptual, and latency boundaries within which computation-elimination techniques are permitted.

If a candidate execution fails to prove compliance with its contract, the runtime **fails closed**: the candidate is rejected and the engine executes the exact fallback routine.

---

## 2. Formal Contract Schema

```python
@dataclass
class Contract:
    name: str                              # Unique identifier for the contract
    exact_required: bool                   # If True, no approximation or perceptual deviation is permitted
    max_abs_error: float | None            # Maximum allowable absolute error |y_approx - y_exact|
    max_relative_error: float | None       # Maximum allowable relative Frobenius / L2 error
    max_rmse: float | None                 # Maximum allowable root-mean-square error
    min_psnr: float | None                 # Minimum peak signal-to-noise ratio (dB) for perceptual data
    min_ssim: float | None                 # Minimum structural similarity index [0.0, 1.0]
    min_accuracy: float | None             # Minimum task accuracy [0.0, 1.0] for classification
    min_recall: float | None               # Minimum top-k recall [0.0, 1.0] for retrieval
    max_latency_ms: float | None           # Maximum allowable wall-clock latency in milliseconds
    min_throughput: float | None           # Minimum required throughput (tokens/sec or ops/sec)
    max_memory_bytes: int | None           # Maximum RAM budget in bytes
    allow_cache: bool                      # Whether exact cache hits may satisfy this contract
    allow_prediction: bool                 # Whether predictive extrapolation is permitted
    allow_approximation: bool              # Whether quantization or low-rank factorization is permitted
    allow_perceptual_difference: bool      # Whether perceptual compression (SSIM/PSNR) is permitted
```

---

## 3. Validation Rules (Fail-Closed)

The function `validate_contract(contract: Contract)` enforces consistency:

1. **Exactness Invariance**: If `exact_required=True`, both `allow_approximation` and `allow_perceptual_difference` MUST be `False`. Contradictory specifications raise `ValueError`.
2. **Non-Negative Errors**: `max_abs_error`, `max_relative_error`, `max_rmse`, and `min_psnr` must be $\ge 0.0$.
3. **Normalized Ranges**: `min_ssim`, `min_accuracy`, and `min_recall` must reside in the closed interval $[0.0, 1.0]$.
4. **Positive Resources**: `max_latency_ms`, `min_throughput`, and `max_memory_bytes` must be $> 0$.

---

## 4. Standard Contract Profiles

| Profile Name | Exact Required | Max Rel Error | Min SSIM | Allow Cache | Allow Approx | Allow Pred | Typical Workload |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`Scientific_Exact`** | `True` | `0.0` | `1.0` | `True` | `False` | `False` | Physics simulation, financial ledger, security tokens |
| **`LLM_Inference_Fast`** | `False` | `0.05` | N/A | `True` | `True` | `True` | Speculative drafting, conversational agents |
| **`Vision_Perceptual`** | `False` | `0.08` | `0.95` | `True` | `True` | `False` | Video stream enhancement, 2D/3D rasterization |
| **`Retrieval_Dense`** | `False` | `0.05` | N/A | `True` | `True` | `False` | Vector search, embedding retrieval (Recall@10 $\ge 0.95$) |
