# 🏛️ HYPER-100: Reproduction Guide & Commands

## 1. Step-by-Step Reproduction

All results, measurements, and tests are completely reproducible on Windows 11 with Python 3.11+ / Node.js 18+.

```powershell
# 1. Run Master Benchmark across all 15 workloads
python -m hyper.benchmark.master_benchmark

# 2. Run Backend Pytest Suite
python -m pytest tests/test_c_gace_engine.py tests/test_breakthrough_dashboard_api.py -v

# 3. Run Frontend Vitest Suite
npx vitest run

# 4. Execute Self-Falsification Suite
python -c "from hyper.adversarial import AdversarialFalsificationSuite; print(AdversarialFalsificationSuite().run_all_adversarial_tests())"
```
