# HYPER / LEO Parity Specification & Four-Score Model

## 1. The Four Independent Parity Metrics
In strict adherence to Sections 21, 30, and 31 of the Master Evolution Protocol, HYPER publishes **four independent, unmixed parity metrics**. Under no circumstances are these four metrics averaged into a single misleading number.

---

### Metric 1: RAW HARDWARE PARITY
$$\text{Raw Hardware Parity} = \frac{\text{Candidate Physical Throughput on Host Silicon}}{\text{Reference Physical Throughput on Target Reference Silicon}}$$
- **Scope**: Direct wall-clock physical throughput comparison executing the identical computation without algorithmic shortcuts.
- **Physical Reality**: An Intel Core i5-12450H CPU + Intel UHD Graphics (48 EUs) provides ~0.8 TFLOPS FP32 vs ~82 TFLOPS FP32 on an NVIDIA RTX 4090. Physical raw throughput ratio is $\approx 1.0\% - 2.5\%$.
- **Invariant**: The system **never** lies about raw hardware parity. Cache hits, low-rank shortcuts, smaller models, or approximations must NEVER be substituted to inflate raw hardware parity.

---

### Metric 2: EXACT COMPUTATIONAL PARITY
$$\text{Exact Computational Parity} = \begin{cases} 100\% & \text{if output is bit-identical and computation is mathematically identical} \\ 0\% & \text{otherwise} \end{cases}$$
- **Scope**: Applies when the contract demands strict mathematical equivalence (`EXACT`).
- **Condition**: Bit-exact equality of output tensors across hardware, or proven discrete mathematical isomorphism.

---

### Metric 3: CONTRACT PARITY
$$\text{Contract Parity} = \begin{cases} 100\% & \text{if } \forall k \in \mathcal{K}, \ \mathrm{Metric}_k(Y_{\text{cand}}, Y_{\text{ref}}) \le \text{Threshold}_k \text{ and } \text{Latency} \le \text{SLO} \\ 0\% & \text{otherwise} \end{cases}$$
- **Scope**: Determines whether the candidate computational pathway satisfies every declared invariant in the formal `ContractIR`:
  - Relative numerical error $\le \epsilon$
  - Perceptual quality $\ge \text{SSIM}_{\min}$
  - Latency $\le \text{SLO}_{\max}$
  - Memory $\le \text{Budget}_{\max}$
- **Core Principle**: A cheaper, transformed pathway (e.g. SVD low-rank or INT4 quantization) can achieve **100% Contract Parity** without executing identical FLOPs.

---

### Metric 4: APPLICATION PERFORMANCE PARITY
$$\text{Application Parity} = \min\left(100\%, \frac{\text{Achieved Application Metric}}{\text{Required Application SLO}}\right)$$
- **Scope**: End-user experiential SLA attainment (e.g. interactive LLM text generation $\ge 25$ tokens/sec, video playback $\ge 60$ FPS, UI responsiveness $\le 16$ ms).

---

### Metric 5 (Supporting): WORK ELIMINATION RATIO
$$\text{Work Elimination Ratio} = 1.0 - \frac{\text{Measured Necessary Work (FLOPs)}}{\text{Reference Brute-Force Work (FLOPs)}}$$
- **Scope**: Measures the fraction of brute-force reference arithmetic rendered mathematically unnecessary by the Information Boundary and Necessity engines.
