# HYPER Benchmark Protocol: Track Isolation & Reproducibility

## 1. Strict Track Separation

To ensure scientific honesty and prevent contamination:

### Track A: EXACT COMPUTATION
- **Rule**: Must execute identical mathematical operations on identical inputs, producing identical outputs within standard floating-point roundoff ($10^{-5}$).
- **Prohibited**: Approximations, downsampling, denoising, low-rank truncation, lossy quantization.
- **Objective**: Measure raw algorithmic and kernel implementation efficiency on Intel CPU + iGPU.

### Track B: CONTRACT-AWARE COMPUTATION
- **Rule**: Algorithmic substitutions, low-rank factorization, sparse transforms, and neural denoising are permitted **provided** the output satisfies the contract ($\text{Error} \le \epsilon$, $\text{SSIM} \ge 0.95$, $\text{PSNR} \ge 35\text{ dB}$).
- **Objective**: Measure real-world application computational sufficiency.

---

## 2. Scientific Benchmark Measurement Rules

1. **Zero Hardcoded Timers**: Every latency, FPS, or throughput figure must be derived from `time.perf_counter()` or platform telemetry.
2. **Cold vs Warm Runs**: Always execute 3 warmup iterations to prime caches and JIT compilations, followed by 10 measured repetitions recording minimum, median, and 95th-percentile execution times.
3. **Hardware Telemetry Recording**: Every benchmark run records exact CPU package power, core frequency, memory utilization, and thread affinity.
