# 🏛️ HYPER-100: Reproduction Guide & Commands

$$\boxed{\textbf{REPRODUCIBLE EXECUTION PROTOCOL}}$$

## 1. Prerequisites & Environment Setup

- Python 3.11+ / 3.13
- Node.js 18+ / 20+

## 2. One-Command Master Benchmark Execution

Run the full 15-workload benchmark suite:

```powershell
python -m hyper.benchmark.master_benchmark
```

This executes all algorithms, records wall-clock latencies, calculates CER, and writes `HYPER_100_RESULTS.json`.

## 3. Automated Test Suites Execution

Run Python pytest and TypeScript Vitest suites:

```powershell
python -m pytest tests/test_c_gace_engine.py tests/test_breakthrough_dashboard_api.py -v
npx vitest run
```

## 4. Run Self-Falsification Hostile Tests

```powershell
python -c "from hyper.adversarial.falsification_suite import AdversarialFalsificationSuite; print(AdversarialFalsificationSuite().run_all_adversarial_tests())"
```

## 5. Web Interface & Studio Launch

Launch the interactive web application:

```powershell
npm run dev
```

Navigate to:

- `http://localhost:3000/breakthrough` (Public Master Studio & NVIDIA Matrix)
- `http://localhost:3000/app/caao-breakthrough` (Authenticated C-GACE Studio)
