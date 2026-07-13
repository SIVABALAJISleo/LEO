# LEO AI v∞ Benchmark Methodology

This document details the metrics, setups, and measurement processes of the LEO AI v∞ reproducible benchmarking suite.

---

## 1. Metrics Measured

- **Model Load Time**: Time required to parse the GGUF header and map weights into memory.
- **Cold Start Latency**: Full startup initialization time (importing libraries + loading model).
- **Time to First Token (TTFT)**: Latency elapsed from submitting query to the first token emitted.
- **Generation Speed (Tokens/Sec)**: Average token throughput rate during active generation.
- **Memory Footprint**: Active physical RAM consumed by the process.
- **CPU/iGPU Utilization**: Metric loads tracked via `psutil` core sweeps.

---

## 2. Measurement Safety Controls

To guarantee authentic and transparent results, LEO implements these rules:
- **Warm-Up Execution**: The benchmark runs 3 warm-up prompts before measuring to trigger JIT compilation and memory pre-allocation.
- **Simulated Metrics Marking**: If the target model GGUF file is missing, the suite reports estimations based on i5-12450H CPU profiles, tagged clearly as `ESTIMATED` to distinguish from `MEASURED` data.
- **Separate Cache Metrics**: Avoids inflating throughput numbers by tracking cache hit latency independently from active generation.
