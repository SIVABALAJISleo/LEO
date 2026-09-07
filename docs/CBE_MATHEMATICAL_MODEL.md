# LEO Compute-Budget Elimination Engine (CBE) — Mathematical Model

## 1. Formal Optimization Problem

The central thesis of the Compute-Budget Elimination Engine is to cast frame generation as a constrained optimization problem. Rather than rendering all pixels at maximum Monte Carlo samples, the engine solves:

$$\min_{\mathbf{a} \in \mathcal{A}} \quad C_{\text{total}}(\mathbf{a}) = C_{\text{render}}(\mathbf{a}) + C_{\text{prediction}}(\mathbf{a}) + C_{\text{reconstruction}}(\mathbf{a}) + C_{\text{memory}}(\mathbf{a}) + C_{\text{control}}(\mathbf{a})$$

$$\text{subject to} \quad \begin{cases}
\mathcal{Q}(I_{\text{output}}, I_{\text{reference}}) \ge Q_{\text{target}} & (\text{Visual Quality Constraint: e.g. SSIM} \ge 0.90) \\
\mathcal{L}(I_{\text{output}}) \le L_{\text{target}} & (\text{Latency Constraint: e.g.} \le 16.67\text{ ms for 60 FPS}) \\
\mathcal{S}(I_{\text{output}}, I_{t-1}) \le S_{\text{target}} & (\text{Temporal Stability Constraint: Flicker} \le 0.03) \\
\mathcal{T}_{\text{package}} \le T_{\text{max}} & (\text{Thermal Constraint: e.g. Package Temp} \le 85^\circ\text{C})
\end{cases}$$

Where $\mathbf{a} \in \mathcal{A}$ is the action vector selected by the contextual bandit workload controller:
$$\mathbf{a} = \left[\text{Tier } k \in \{0, \dots, 7\}, \; s \in [0.33, 1.0], \; \mathbf{VRS} \in \{1\times 1, 2\times 2, 4\times 4\}, \; \text{spp} \in \{1, 2, 4, 32\}\right]$$

---

## 2. Compute Elimination Ratio (CER) Formulation

### 2.1 The Ray Elimination Ratio
Let $W, H$ be the frame width and height, and $\text{spp}_{\text{target}}$ be the reference sample count (e.g. 32 SPP). The baseline ray budget is:
$$C_{\text{baseline}}^{\text{rays}} = W \times H \times \text{spp}_{\text{target}}$$

Let $N_{\text{actual}}^{\text{rays}}$ be the actual rays cast across all sparse residual tiles and sub-sampled grids. The Ray CER is:
$$\text{CER}_{\text{rays}} = 1.0 - \frac{N_{\text{actual}}^{\text{rays}}}{C_{\text{baseline}}^{\text{rays}}}$$

### 2.2 The Net Latency CER (Strict Non-Double-Counting)
To ensure absolute scientific honesty, net acceleration must account for all algorithm overheads:
$$C_{\text{actual}}^{\text{net}} = t_{\text{render}} + t_{\text{state\_diff}} + t_{\text{prediction}} + t_{\text{reconstruction}} + t_{\text{control}}$$

$$\text{CER}_{\text{net}} = \max\left(0.0, \; 1.0 - \frac{C_{\text{actual}}^{\text{net}}}{t_{\text{baseline\_render}}}\right)$$

No savings are double-counted: every millisecond spent on prediction or reconstruction directly penalizes $\text{CER}_{\text{net}}$.

---

## 3. Spatiotemporal Importance Field

The perceptual priority field $\mathcal{I}(x, y) \in [0, 1]$ steers compute to where human vision has the highest sensitivity:

$$\mathcal{I}(x, y) = \text{clamp}\left(w_p \mathcal{I}_p(x, y) + w_s \mathcal{I}_s(x, y) + w_m \mathcal{I}_m(x, y), \; 0, \; 1\right)$$

Where:
- **Perceptual Saliency $\mathcal{I}_p$**: High-frequency luminance gradient magnitude:
  $$L(x, y) = 0.299 R + 0.587 G + 0.114 B, \quad \mathcal{I}_p(x, y) = \|\nabla L(x, y)\|$$
- **Semantic Priority $\mathcal{I}_s$**: Look-up weighting by object category:
  $$\mathcal{I}_s(x, y) = \omega_{\text{class}}(\text{instance}(x, y)), \quad \omega \in [0.1, 1.0]$$
- **Motion Saliency $\mathcal{I}_m$**: Projected pixel displacement:
  $$\mathcal{I}_m(x, y) = \min\left(1.0, \; \frac{\|\mathbf{v}(x, y)\|}{v_{\text{max}}}\right)$$

---

## 4. Spatiotemporal Reprojection & History Clamping

### 4.1 Sub-pixel Motion-Compensated Warping
Given motion vector field $\mathbf{v}(x, y) = (\Delta x, \Delta y)$, the previous frame sample location is:
$$\mathbf{x}_{t-1} = \mathbf{x}_t - \mathbf{v}(\mathbf{x}_t)$$

The reprojected color $I_{\text{reproj}}(\mathbf{x}_t)$ is sampled via bilinear interpolation over the 4 nearest neighbors:
$$I_{\text{reproj}}(\mathbf{x}_t) = \sum_{i \in \{0, 1\}} \sum_{j \in \{0, 1\}} w_{ij} I_{t-1}(\lfloor x_{t-1} \rfloor + i, \lfloor y_{t-1} \rfloor + j)$$

### 4.2 Disocclusion Metric
A pixel is classified as disoccluded if the relative depth delta violates surface continuity:
$$\mathcal{D}(\mathbf{x}_t) = \mathbb{I}\left( \frac{|z_t(\mathbf{x}_t) - z_{t-1}(\mathbf{x}_{t-1})|}{\max(|z_t(\mathbf{x}_t)|, \epsilon)} > \tau_z \right)$$

Where $\tau_z = 0.05$ (5% depth tolerance). Disoccluded pixels receive confidence $c(\mathbf{x}_t) = 0$.

### 4.3 AABB Color Box Clamping (Ghosting Kill Operator)
To prevent ghosting artifacts when surfaces or lighting change, the reprojected color is clamped to the local $3 \times 3$ neighborhood box in the current frame's guide color:
$$\mathbf{b}_{\text{min}}(\mathbf{x}_t) = \min_{\mathbf{p} \in \mathcal{N}_3(\mathbf{x}_t)} I_{\text{guide}}(\mathbf{p}), \quad \mathbf{b}_{\text{max}}(\mathbf{x}_t) = \max_{\mathbf{p} \in \mathcal{N}_3(\mathbf{x}_t)} I_{\text{guide}}(\mathbf{p})$$

$$I_{\text{clamped}}(\mathbf{x}_t) = \text{clip}\left(I_{\text{reproj}}(\mathbf{x}_t), \; \mathbf{b}_{\text{min}}(\mathbf{x}_t), \; \mathbf{b}_{\text{max}}(\mathbf{x}_t)\right)$$

---

## 5. ReSTIR Spatiotemporal Reservoir Sampling

Reservoir sampling maintains unbiased Monte Carlo estimates using streaming candidate selection.

### 5.1 Weight Update Rule
For a sample stream $y_1, \dots, y_M$ with target distribution $\hat{p}(y)$ and proposal distribution $p(y)$:
$$w_i = \frac{\hat{p}(y_i)}{p(y_i)}$$

Each reservoir $R = (y, w_{\text{sum}}, M, W)$ updates as:
$$w_{\text{sum}} \leftarrow w_{\text{sum}} + w_i, \quad M \leftarrow M + 1$$
$$y \leftarrow y_i \quad \text{with probability} \quad \frac{w_i}{w_{\text{sum}}}$$

The unbiased normalization weight $W$ is:
$$W = \frac{w_{\text{sum}}}{M \cdot \hat{p}(y)}$$

### 5.2 Spatiotemporal Combination
Given temporal reservoir $R_t$ and spatial neighbor reservoirs $R_{s, 1}, \dots, R_{s, K}$, candidates are combined by summing weights:
$$w_{\text{comb}} = \sum_{k=1}^K w_{\text{sum}, k}, \quad M_{\text{comb}} = \sum_{k=1}^K M_k$$

Coplanarity rejection enforces that reservoirs are only exchanged if surface normals satisfy:
$$\mathbf{n}_i \cdot \mathbf{n}_j \ge 0.90 \quad \text{and} \quad \frac{|z_i - z_j|}{z_i} \le 0.10$$

---

## 6. Contrast Adaptive Sharpening (CAS)

The CAS sharpening operator enhances edge contrast while preventing overshoot and haloing.
For a 5-tap cross neighborhood $(C, T, B, L, R)$:
$$m_{\text{min}} = \min(C, T, B, L, R), \quad m_{\text{max}} = \max(C, T, B, L, R)$$
$$\text{amp} = \frac{\min(m_{\text{min}}, 1.0 - m_{\text{max}})}{\max(m_{\text{max}}, 10^{-4})}$$
$$w = -\sqrt{\text{clamp}(\text{amp}, 0, 1)} \cdot (\sigma_{\text{sharp}} \cdot 0.1875)$$
$$I_{\text{sharp}} = \frac{C + w(T + B + L + R)}{1 + 4w}$$
