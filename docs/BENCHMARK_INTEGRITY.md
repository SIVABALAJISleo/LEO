# HYPER / LEO — Anti-Benchmark-Gaming & Integrity Standard
**Document Version:** 2.0.0 (Ultra-Sonic Master Engineering)

---

## 1. Prohibited Benchmark Gaming Practices

HYPER's automated verification framework actively detects and rejects the following 18 benchmark gaming practices:

1. **Workload Alteration**: Reducing matrix dimensions or dataset size between candidate and reference runs.
2. **Dimension Truncation**: Cutting off sequence lengths or hidden dimensions to inflate tokens/sec.
3. **Reduced Sample Counts**: Benchmarking fewer iterations than declared in the frozen manifest.
4. **Quality Degradation**: Subtly dropping numerical precision without declaring `BOUNDED_APPROXIMATION`.
5. **Model Downscaling**: Silently swapping a 1.5B model for a 0.5B model.
6. **Context Truncation**: Dropping attention context window during generation.
7. **Hidden Caching**: Warming caches prior to cold benchmark execution.
8. **Warm-Cache Contamination**: Disguising cached lookup latency as arithmetic compute throughput.
9. **Simulated Timing**: Using analytical or synthetic sleep calls instead of `time.perf_counter()`.
10. **Hardcoded Timing**: Inserting pre-baked latency numbers.
11. **Reference Constants**: Hardcoding reference outputs rather than computing trusted baselines.
12. **Candidate/Reference Identity**: Comparing `fn(A, B)` against `fn(A, B)` to force a false pass.
13. **Omitted Preprocessing**: Excluding tokenization or data layout conversion from end-to-end timing.
14. **Omitted Postprocessing**: Excluding detokenization, detiling, or output format normalization.
15. **Omitted Transfer Overhead**: Ignoring host-to-device buffer copy times.
16. **Omitted Verification Time**: Hiding audit and verification costs from latency budgets.
17. **Cherry-Picked Outliers**: Reporting the single best run rather than P50/P90/P99 distributions.
18. **Invalid Hardware Metadata**: Reporting execution on hardware differing from the host CPU/iGPU.
