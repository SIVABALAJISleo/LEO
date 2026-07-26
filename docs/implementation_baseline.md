# LEO AI v∞ Implementation Baseline Report

## Repository Architecture & Entry Points

The workspace is organized into a modular layered architecture optimized for CPU and offline execution:

- **`/backend/main.py`**: Principal FastAPI entry point serving API routes.
- **`/backend/routers/`**: HTTP dispatchers (`orchestrate.py`, `system.py`, etc.).
- **`/backend/hardware/`**: Hardware detection (`detector.py`) and execution ranking (`router.py`).
- **`/core_ai/`**: Deep compute engines including speculative decoding (`speculative_decoder.py`), custom AVX JIT kernels (`custom_kernels.py`), memory pooling (`cache_manager.py`), and scheduling (`task_scheduler.py`).
- **`/experts/`**: Domain expert modules (`domain_experts.py`) and semantic MOE routing (`router.py`).
- **`/backend/intelligence/`**: Document parsers (`document_processor.py`) and indexed retrieval (`knowledge_engine.py`).
- **`/tests/`**: Custom pytest suite checking component functionality.

## Backend and Frontend Launch Commands

- **Backend Launch**: `python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000`
- **Frontend Launch**: `npm run dev` (run from root workspace context)

## Existing Model Files

- `models/leo_bitnet.gguf` (23.3 MB): Mock quantization weights.
- `models/leo_original.pt` (93.3 MB): Initial mock model state.
- `models/leo-3b-1.58bit/config.json` (62 bytes): Model configuration settings.

## Forensics: Mocks, Placeholders, and Dependency Status

- **Speculative decoding speedups**: Previously emulated speedups (`8.2 + np.random.uniform(0.0, 0.4)`) inside `core_ai/speculative_decoder.py` to simulate token performance.
- **Heterogeneous speeds**: Previously simulated 2.5x to 3.0x speedups inside `core_ai/heterogeneous_orchestrator.py` when OpenVINO was not found.
- **Python version**: Python 3.13.5 (verified via pytest output).
- **Installed Typecheckers/Linters**: Ruff 0.15.20 is installed under the Python environment.

## Current Test Status

- `pytest tests/test_*.py` - **26 passed** (100% correct component execution).
- `_run_integration_tests.py` - **ALL TESTS PASSED [OK]** (validating API endpoints and multilingual Dravidian language routes).
