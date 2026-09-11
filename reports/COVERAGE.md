# LEO / HYPER: Multi-Dimensional Coverage Report

**Document**: `reports/COVERAGE.md`  
**Version**: 1.0.0  
**Principle**: The system strictly separates coverage dimensions rather than reporting a single vanity number.

---

## 1. Five Independent Coverage Dimensions

```
+--------------------------------------------------------------+
|             LEO / HYPER COVERAGE SCORECARD                   |
+--------------------------------------------------------------+
| 1. Contract Coverage:        100.0% (6 / 6 Workloads Closed) |
| 2. Necessity Coverage:       100.0% (24 / 24 Ops Classified) |
| 3. Application Coverage:      83.3% (5 / 6 Domains Active)   |
| 4. Verification Coverage:    100.0% (56 / 56 Adversarial OK) |
| 5. Benchmark Coverage:       100.0% (6 / 6 Physically Run)   |
+--------------------------------------------------------------+
```

---

## 2. Dimension Breakdown

- **Contract Coverage ($100.0\%$)**:
  Every evaluated workload produced an unambiguous outcome: `WORMHOLE_FOUND` (4 workloads) or `NECESSARY_COMPUTATION_IDENTIFIED` (2 workloads). Zero inconclusive workloads remain.
- **Necessity Coverage ($100.0\%$)**:
  Every node in the computational DAG is classified into `REQUIRED`, `REDUNDANT`, `REUSABLE`, `PREDICTABLE`, or `APPROXIMABLE`. Zero nodes remain in the `UNKNOWN` classification.
- **Application Coverage ($83.3\%$)**:
  Active domain adapters exist for Dense Linear Algebra, Sparse Matrix-Vector, Scientific Stencils, Graphics Viewports, and AI Inference. Search/RAG is registered in the universe.
- **Verification Coverage ($100.0\%$)**:
  All 13 adversarial failure modes passed without regression.
- **Benchmark Coverage ($100.0\%$)**:
  All 6 core universe entries have physical latency and memory measurements recorded on the target host.
