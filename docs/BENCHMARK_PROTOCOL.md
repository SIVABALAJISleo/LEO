# HYPER Multi-Dimensional Benchmark & Anti-Cheating Protocol

## 1. Core Principles of Benchmark Integrity

A benchmark without strict execution discipline is an illusion. The HYPER benchmark suite enforces rigorous scientific integrity to ensure that measured performance gains reflect genuine algorithmic and architectural discoveries rather than measurement artifacts or deceptive practices.

---

## 2. Execution Discipline & Cache States

Every benchmark execution must explicitly declare and control its cache state:

| Cache State | Definition | Measurement Discipline |
| :--- | :--- | :--- |
| **`COLD`** | All CPU caches flushed, zero memory buffers pre-allocated, OS file caches purged. | Measures raw latency including allocation and cold instruction fetching. |
| **`WARM`** | Instruction caches primed, memory pages mapped, JIT compiled (if applicable). | Measures steady-state repetitive computational throughput. |
| **`CACHED`** | Prior results or intermediate lookup tables available in RAM. | Permitted ONLY when the workload contract explicitly permits caching. |
| **`INCREMENTAL`**| Only updated state or deltas processed relative to prior frame $t-1$. | Permitted for streaming, video, and animation workloads. |

**Strict Rule**: Never compare a `CACHED` candidate pathway against a `COLD` baseline. Doing so immediately triggers an `INVALID_COMPARISON` benchmark violation.

---

## 3. Automated Anti-Cheating Engine

The `BenchmarkFairnessEngine` automatically monitors execution and flags fraudulent benchmark comparisons:

1. **Input Tampering Detection**:
   Computes SHA-256 hashes of input arrays before and after candidate execution. Any modification of inputs without contract permission triggers `FLAG: INPUT_TAMPERED`.
2. **Output Truncation / Precision Downgrade**:
   Detects if a candidate achieved speedup simply by computing a smaller fraction of the required output or truncating precision (e.g. silently returning FP16 when FP64 was contracted). Triggers `FLAG: PRECISION_DOWNGRADED`.
3. **Hidden Hardware Invocation**:
   Monitors system telemetry during execution to confirm that compute is executed exclusively on the local Intel Core i5-12450H CPU and Intel UHD iGPU. Any offloading to external servers or discrete GPUs triggers `FLAG: EXTERNAL_OFFLOAD_DETECTED`.
4. **Precomputation Leaks**:
   Detects if a candidate uses lookup tables whose size or generation time exceeded the benchmark budget. Triggers `FLAG: HIDDEN_PRECOMPUTATION`.

---

## 4. Multi-Dimensional Metrics

Benchmark reports must present independent measurements across all critical physical dimensions rather than aggregating them into a single misleading score:

1. **Latency**: Minimum, median, mean, P95, and P99 wall-clock execution time (milliseconds).
2. **Throughput**: Elements, pixels, or operations processed per second.
3. **Memory Footprint**: Working set size and peak resident set size (Peak RSS in MB).
4. **Memory Bandwidth**: Measured gigabytes per second moved across system buses.
5. **CPU Utilization**: Core residency across P-cores and E-cores.
6. **Integrated GPU Utilization**: EU activity and OpenCL kernel dispatch latency.
7. **Energy Consumption**: Measured CPU/iGPU package energy draw in Joules.
8. **Numerical Stability**: Maximum absolute error ($\epsilon_{max}$), mean squared error (MSE), and relative drift.
9. **Measurement Reproducibility**: Variance ratio across multiple independent execution runs.

---

## 5. Distinct Parity Metric Reporting

To maintain total transparency, HYPER reports parity across eight distinct, non-fungible metrics:

```
┌────────────────────────────────────────────────────────┐
│             HYPER 8-DIMENSION PARITY MATRIX            │
├─────────────────────────┬──────────────────────────────┤
│ 1. Hardware Parity      │ NOT_ACHIEVED (Disjoint)      │
│ 2. Computational Parity │ MEASURED (Workload-specific) │
│ 3. Contract Parity      │ VERIFIED (Meets tolerances)  │
│ 4. Numerical Parity     │ VERIFIED (Tolerance bound)   │
│ 5. Performance Parity   │ WORKLOAD-DEPENDENT           │
│ 6. Resource Parity      │ MEASURED (RAM / Wattage)     │
│ 7. Energy Parity        │ MEASURED (Package Joules)    │
│ 8. Universal Parity     │ UNPROVEN (Active Search)     │
└─────────────────────────┴──────────────────────────────┘
```
