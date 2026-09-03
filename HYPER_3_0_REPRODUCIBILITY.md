# HYPER 3.0: Reproduction Guide & Protocol

## Environment Requirements
- Python 3.10+
- NumPy, SciPy, PyTorch CPU, OpenVINO, FastAPI, Pytest
- Host: Windows 11 (AMD64) or Linux x86_64

## Execution Commands
```bash
# 1. Run full test suite
python -m pytest tests/test_hyper_v3_*.py -v

# 2. Run CLI benchmark
python scripts/hyper3_cli.py benchmark

# 3. Run audit report generation
python scripts/hyper3_cli.py audit

# 4. Start API backend
uvicorn backend.main:app --port 8000
```
