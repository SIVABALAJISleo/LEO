# HYPER: Independent Verification Engine Specification

## 1. Verification Principles
1. **Independent Reference Path**: The verifier executes separate validation algorithms that do not share intermediate memory or buffers with the optimizer.
2. **Sub-linear Verification**: For operations where full recalculation would erase optimization gains (e.g. matrix multiplication), the verifier employs randomized sub-linear algorithms.
3. **Multi-Domain Coverage**: Verification methods are domain-specialized (algebraic, symplectic, perceptual, statistical).

---

## 2. Mathematical Verification Methods

### A. Freivalds Randomized Matrix Multiplication Check
To verify $A \cdot B = C$ for $N \times N$ matrices in $O(k \cdot N^2)$ rather than $O(N^3)$:
1. Choose $k$ random binary vectors $r \in \{0, 1\}^N$.
2. Compute $v_1 = A \cdot (B \cdot r)$ and $v_2 = C \cdot r$.
3. If $v_1 = v_2$ for all $k$ rounds, $C$ is correct with error probability $P(\text{error}) \le 2^{-k}$. For $k=5$, $P(\text{error}) < 0.03125$.

### B. Symplectic Energy Drift (N-Body & Particle Physics)
Physical dynamical systems conserve Hamiltonian energy $H(p, q)$. The verifier measures fractional energy drift:
$$\Delta E = \frac{|E_{\text{final}} - E_{\text{initial}}|}{\max(E_{\text{initial}}, 10^{-6})} \le 0.05$$

### C. Structural Similarity Index (SSIM - Rendering & Video)
For image and rendering outputs, pointwise MSE is often misleading. The verifier computes 2D structural luminance, contrast, and structure:
$$\text{SSIM}(x, y) = \frac{(2\mu_x\mu_y + c_1)(2\sigma_{xy} + c_2)}{(\mu_x^2 + \mu_y^2 + c_1)(\sigma_x^2 + \sigma_y^2 + c_2)} \ge 0.85$$

### D. Metamorphic Testing
Verifies mathematical invariances (scale linearity, translation invariance, permutation equivariance) across randomized inputs.
