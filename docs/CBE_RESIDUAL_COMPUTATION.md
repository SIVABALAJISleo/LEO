# LEO CBE — Residual Computation & Sparse Scheduling Specification

## 1. Concept: Rendering Only What Changed

In typical graphical rendering, up to $80\text{--}95\%$ of screen pixels remain identical or predictably correlated with previous frames. The **LEO CBE Residual Subsystem** decomposes frames into discrete $16 \times 16$ screen-space tiles and computes exact and predictive delta metrics to isolate and render only volatile or newly uncovered geometry.

---

## 2. Formal 9-Class Residual Hierarchy

Each $16 \times 16$ tile is classified into one of 9 mutually exclusive behavioral categories:

| Class ID | Class Name | Compute Action | Expected CER |
|---|---|---|---|
| 0 | `UNCHANGED` | Direct temporal cache reuse. No rays fired. | $100\%$ |
| 1 | `REPROJECTABLE` | Motion-compensated bilinear reprojection from history. | $100\%$ |
| 2 | `PREDICTABLE` | Kinematic future extrapolation from previous velocity vectors. | $90\text{--}95\%$ |
| 3 | `SHADING_RESIDUAL` | Indirect lighting query from 6D spatial hash radiance cache. | $75\text{--}85\%$ |
| 4 | `GEOMETRY_DISOCCLUSION`| Newly revealed background. Sparse raytrace (2 SPP) + spatial fill. | $50\text{--}70\%$ |
| 5 | `SPECULAR_SURFACE` | View-dependent highlight change. Coarse VRS ray trace (2x2). | $40\text{--}60\%$ |
| 6 | `HIGH_FREQUENCY` | Complex edge texture. Full-resolution 4 SPP ray trace. | $25\text{--}40\%$ |
| 7 | `NEW_INSTANCE` | Newly spawned entity. Full path trace (4--8 SPP). | $0\text{--}20\%$ |
| 8 | `VOLATILE_PARTICLE` | Alpha transparency / particle effects. Perceptual bypass. | $10\text{--}30\%$ |

---

## 3. Residual Classification Invariants

A tile $T_{k}$ with mean pixel delta $\delta_k = \frac{1}{|T_k|} \sum_{\mathbf{p} \in T_k} |I_t(\mathbf{p}) - I_{\text{reproj}}(\mathbf{p})|$ and mean motion velocity $\bar{v}_k$ is classified via hierarchical decision tree:

$$\text{Class}(T_k) = \begin{cases}
\text{UNCHANGED} & \text{if } \delta_k < 0.005 \text{ and } \bar{v}_k < 0.01 \\
\text{REPROJECTABLE} & \text{if } \delta_k < 0.030 \text{ and } \bar{c}_k \ge 0.85 \\
\text{PREDICTABLE} & \text{if } \delta_k < 0.080 \text{ and } \bar{v}_k \text{ is constant} \\
\text{GEOMETRY\_DISOCCLUSION} & \text{if } \text{disoccluded\_ratio} > 0.25 \\
\text{SPECULAR\_SURFACE} & \text{if } \text{is\_roughness\_low} \text{ and } \delta_k > 0.10 \\
\text{HIGH\_FREQUENCY} & \text{if } \text{variance}(T_k) > \tau_{\text{var}} \\
\text{NEW\_INSTANCE} & \text{otherwise}
\end{cases}$$

Tiles requiring compute are dispatched to a priority queue sorted by $\mathcal{I}(T_k) \cdot \delta_k$. If the stage compute budget expires, remaining low-importance tiles are reconstructed via spatial cross-bilateral inpainting, guaranteeing strict 60 FPS pacing.
