# LEO/HYPER CORRECTNESS AND VERIFICATION MODEL

**Module Reference:** `hyper.verification.verifier`  
**Standard:** Phase 12 Multi-Domain Verification Standard  

---

## 1. Multi-Domain Verification Hierarchy

LEO/HYPER establishes five formal verification layers tailored to distinct numerical and perceptual workload domains:

```text
                     [OUTPUT TENSOR / VALUE]
                               │
       ┌───────────────────────┼───────────────────────┐
       ▼                       ▼                       ▼
[1. EXACT NUMERICAL]    [2. FREIVALDS MATRIX]   [3. PERCEPTUAL SSIM/PSNR]
  - max_abs_error         - A(Br) == Cr           - SSIM >= tau
  - relative_error        - Error prob <= 2^-k    - PSNR >= min_db
  - output SHA-256        - O(k N^2) probe        - Pixel delta <= eps
       │                       │                       │
       └───────────────────────┼───────────────────────┘
                               ▼
            [4. RETRIEVAL & LLM VERIFICATION]
              - Top-k Recall & Precision
              - Mean Reciprocal Rank (MRR)
              - Token Agreement Rate
```

---

## 2. Mathematical Formulations

### 2.1 Numerical Distance
- **Maximum Absolute Error**:
  $$\max |y_{\text{approx}} - y_{\text{exact}}|$$
- **Relative Error**:
  $$\frac{\|y_{\text{approx}} - y_{\text{exact}}\|_2}{\max(10^{-12}, \|y_{\text{exact}}\|_2)}$$
- **Root Mean Square Error**:
  $$\text{RMSE} = \sqrt{\frac{1}{N} \sum_{i=1}^N (y_i - \hat{y}_i)^2}$$

### 2.2 Freivalds Probabilistic Matrix Product Verification
For matrix product verification $A B \stackrel{?}{=} C$:
1. Sample random vector $r \in \{-1, +1\}^N$.
2. Compute $v_1 = A(Br)$ and $v_2 = Cr$ in $O(N^2)$ time.
3. Check relative residual:
   $$\frac{\|v_1 - v_2\|_2}{\|v_1\|_2} \le \epsilon$$
4. Across $k$ independent trials, the probability of falsely accepting an incorrect matrix product is:
   $$\Pr(\text{false accept}) \le 2^{-k}$$
5. **Scientific Caveat**: Freivalds is a probabilistic guarantee, not a deterministic proof. For $k=5$, $\Pr(\text{undetected error}) \le 0.03125$.

### 2.3 Perceptual Quality (SSIM & PSNR)
- **PSNR**:
  $$\text{PSNR} = 20 \log_{10} \left( \frac{\text{MAX}_I}{\sqrt{\text{MSE}}} \right)$$
- **SSIM**:
  $$\text{SSIM}(x, y) = \frac{(2 \mu_x \mu_y + c_1)(2 \sigma_{xy} + c_2)}{(\mu_x^2 + \mu_y^2 + c_1)(\sigma_x^2 + \sigma_y^2 + c_2)}$$
