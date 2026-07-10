# Contributing to LEO Infinity Kernels

Thank you for your interest in contributing to the LEO Infinity Kernels project!

## Submitting Benchmarks

We welcome benchmark results from different hardware configurations. To submit:

1. Run the benchmark suite:
   ```bash
   python -m leo_infinity_kernels.benchmarks.bench_kernels > my_benchmark.txt
   ```

2. Include your hardware profile:
   - CPU model and generation
   - RAM size
   - iGPU / NPU presence
   - OS version

3. Open a GitHub Issue with the title `[Benchmark] <CPU Model> - <OS>` and attach your results.

## Submitting Kernel Improvements

1. Fork the repository
2. Create a feature branch: `git checkout -b kernel/my-improvement`
3. Add your kernel to `leo_infinity_kernels/leo_infinity_kernels/`
4. Add benchmarks in `leo_infinity_kernels/leo_infinity_kernels/benchmarks/`
5. Run the test suite: `python -m pytest tests/test_infinity_evolution.py -v`
6. Submit a pull request

### Kernel Requirements
- Must be pure Python (NumPy allowed) — no compiled extensions
- Must include a benchmark showing speedup over baseline
- Must include docstrings and type hints
- Must not introduce new required dependencies (optional extras OK)

## Feedback Ingestion

User feedback (benchmark results, edge cases, hardware reports) is automatically ingested into the evolution loop when submitted via:
- The `/api/v1/leo/vinfinity/telemetry` API endpoint
- The `TelemetryCollector.record_inference()` method

This data drives automated weakness detection and parameter evolution.

## Code Style
- Python 3.8+ compatible
- Type hints required
- Docstrings for all public methods
- Follow existing patterns in the codebase

## License
All contributions are licensed under MIT.
