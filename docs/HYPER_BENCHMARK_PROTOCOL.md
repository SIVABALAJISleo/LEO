# HYPER Rigorous Hardware Benchmark Protocol
**Target Machine**: Intel Core i5-12450H (8 Cores, 12 Threads, AVX2/FMA, 16 GB RAM, Windows 11).
**Integrated Graphics**: Intel UHD Graphics (48 EUs, shared system RAM).

---

## 1. Hardware Locking & Provenance Verification

1. **Target Hardware Identification**:
   - Every benchmark run begins by querying CPU model, core/thread topology, RAM capacity, OS version, GPU model, and OpenCL driver via `HardwareFingerprint.detect()`.
   - If the host machine is not an Intel Core i5-12450H (or compatible i5-12th/13th gen architecture), the run is flagged with `TARGET_HARDWARE_MISMATCH`. It may not enter the official target leaderboard.
2. **Real Hardware vs Simulation**:
   - Only physical execution timed on local hardware enters the primary performance leaderboard.
   - Results from emulators, simulators, or synthetic replays are strictly tagged as `SIMULATED`.

---

## 2. Timing & Measurement Methodology

1. **Nanosecond Timer Precision**:
   - All timing intervals are captured using `time.perf_counter_ns()` with microsecond-level precision.
2. **Warmup & Cache Isolation**:
   - **Cold Cache Track (`CACHE_COLD`)**:
     Prior to timing, an orthogonal memory eviction buffer ($> 32\text{ MB}$, larger than the $12\text{ MB}$ CPU L3 cache) is read and written to ensure caches are flushed. First-iteration timing is recorded.
   - **Warm Cache Track (`CACHE_WARM`)**:
     $5$ warmup iterations are executed to achieve steady-state instruction cache and branch predictor priming.
   - **Rule**: Cold cache and warm cache timings must NEVER be averaged or conflated into a single metric.
3. **Statistical Confidence & Outlier Trimming**:
   - Minimum sample count: $N \ge 30$ iterations.
   - Outlier filtering: Discard minimum and maximum values; compute Median, Mean, P95, and P99 latency.

---

## 3. Power & Thermal Telemetry Rules

1. **Physical Sensors**:
   - If Intel RAPL (Running Average Power Limit) or OS battery discharge telemetry is available, report as `MEASURED_POWER`.
2. **Analytical Estimation**:
   - In the absence of direct hardware power sensors, power is analytically estimated from CPU TDP ($45\text{ W}$) and core utilization.
   - **Rule**: Analytical estimates must be labeled strictly as `ESTIMATED_POWER`. Calling an estimate "measured power" constitutes an immediate audit failure.

---

## 4. Endurance & Thermal Throttling Testing

To verify that optimizations sustain real-time performance without memory leaks or thermal throttling:
1. **1-Minute Quick Endurance**: Verifies garbage collection stability and absence of buffer leaks.
2. **10-Minute Sustained Load**: Monitors CPU frequency scaling and thermal throttling on the laptop cooling solution.
3. **30-Minute & 60-Minute Stress Runs**: For production continuous compilation workflows.
   - Criteria: P95 latency must not drift by more than $15\%$ between minute 1 and minute 30.
