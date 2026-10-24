# Rigorous Benchmark Methodology Specification

## 1. Measurement Integrity & Rules

1. **Equal Measurement Boundaries:** Timing measurements for candidate and reference must begin and end at identical lifecycle points. Transfer overhead, initialization, and layout conversions must be included in end-to-end latency.
2. **Multi-Sample Statistics:** Single-run benchmarks are strictly forbidden. A minimum of 5 warmup runs followed by 10 to 100 timed trials is enforced.
3. **Statistical Metrics:**
   - Median Latency ($p_{50}$)
   - Tail Latency ($p_{95}, p_{99}$)
   - Interquartile Range / Standard Deviation
   - Deadline Miss Rate ($\% \text{ of trials exceeding SLA}$)

---

## 2. Speedup Formulation

$$\text{Speedup (Latency)} = \frac{\text{Reference Median Latency (ms)}}{\max(\text{Candidate Median Latency (ms)}, 1\mu s)}$$

$$\text{Speedup (Throughput)} = \frac{\text{Candidate Throughput (ops/s)}}{\max(\text{Reference Throughput (ops/s)}, 1\text{e-6})}$$

- If candidate is slower ($\text{speedup} < 1.0$), it is recorded truthfully as a regression. It is **never** labeled a performance improvement.

---

## 3. Bandwidth Accounting

Physical DDR bus bandwidth is strictly separated from algorithmic data avoidance:

- **Measured Bus Bandwidth:** $\frac{\text{Physical Bytes Transferred}}{\text{Wall Clock Time}}$ (typically 15–25 GB/s on dual-channel DDR).
- **Algorithmic Data Avoidance:** Calculated theoretically when intermediate tensors are avoided via kernel fusion or tiling. Algorithmic avoidance is **never** reported as physical bus throughput.
