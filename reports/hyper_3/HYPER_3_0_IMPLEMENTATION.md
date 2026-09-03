# HYPER 3.0: Implementation & Engineering Details

HYPER 3.0 was implemented directly in the LEO / HYPER repository as a high-performance Python package (`hyper_v3/`) backed by NumPy, SciPy, PyTorch CPU, OpenVINO, and FastAPI.

## Codebase Organization
- `hyper_v3/frontend/`: Contract compiler and program observer.
- `hyper_v3/ir/`: Universal computation graph IR.
- `hyper_v3/intelligence/`: 9-dimensional intelligence suite.
- `hyper_v3/proof/`: Proof engine and exactness certificates.
- `hyper_v3/transforms/`: Transformation passes.
- `hyper_v3/search/`: Autotuner and cost models.
- `hyper_v3/runtime/`: Heterogeneous execution runtime.
- `hyper_v3/memory/`: Memory pools and cache hierarchy.
- `hyper_v3/verification/`: Independent verifiers.
- `hyper_v3/workloads/`: 15 regression workloads + holdouts.
- `hyper_v3/benchmark/`: 4-scoreboard evaluation suite.
- `hyper_v3/telemetry/`: Computational work ledger.
- `hyper_v3/learning/`: Hardware profiler and online learning.
- `hyper_v3/audit/`: Report generator and falsification suite.
- `hyper_v3/cli/`: CLI tool.
- `backend/routers/hyper_v3_api.py`: FastAPI endpoints.
