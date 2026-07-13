# LEO AI v∞ Laptop Quickstart Guide

This guide describes how to configure, validate, and execute LEO AI v∞ under offline laptop hardware constraints (Intel Core i5-12450H).

---

## 1. Installation & Doctor Audit
First, verify your system configuration by executing the doctor diagnostic check:

```powershell
python leo.py doctor
```

To output the hardware report formatted as JSON for validation pipelines:
```powershell
python leo.py doctor --json
```

---

## 2. Download and Validate Model
Download the legally suitable Qwen2.5-0.5B-Instruct-GGUF model to the local `models` directory:

- **Target Download Path**: `models/qwen2.5-0.5b-instruct.gguf`
- **HuggingFace Source URL**: `https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct-GGUF/resolve/main/qwen2.5-0.5b-instruct-q4_k_m.gguf`

Verify model integrity against the validation contract (SHA-256 and GGUF structure checks):
```powershell
python leo.py validate --model models/qwen2.5-0.5b-instruct.gguf
```

---

## 3. Run Benchmark Suite
Run the hardware smoke tests to verify latency and throughput (tokens/sec):

```powershell
python leo.py benchmark --suite smoke
```

To run a full sweep measuring p50/p95 latency and save the output report:
```powershell
python leo.py benchmark --suite full --output results/run.json
```

---

## 4. Spin Up the Service
Launch the FastAPI semantic orchestration server optimized under the local laptop profile:

```powershell
python leo.py serve --profile laptop
```

This binds execution to **8 threads** (matching the physical cores of the i5-12450H CPU to avoid hyperthreading bottlenecks).
