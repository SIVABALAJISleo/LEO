# LEO AI v∞ Troubleshooting Guide

Resolve common installation, validation, and performance anomalies on local laptop environments.

---

## 1. Model Validation Faults

### Error: `Model file missing`

- **Cause**: The GGUF model file was not found at the configured path.
- **Resolution**: Download the Qwen2.5-0.5B-Instruct-GGUF model to the designated path. See [Quickstart Laptop Guide](file:///c:/Users/sivab/OneDrive/Documents/HYPER/docs/quickstart_laptop.md) for URLs.

### Error: `Invalid GGUF format`

- **Cause**: File header does not contain GGUF magic bytes (usually means the download failed or file is corrupted).
- **Resolution**: Delete the file and re-download the target model.

---

## 2. Resource Governor Warnings

### Status: `CRITICAL` low RAM warning

- **Cause**: Available system RAM is below 1 GB.
- **Resolution**: Close memory-intensive background apps. LEO automatically triggers aggressive garbage collection, purges caches, and drops concurrency limits to 1 to prevent swap storm crashes.

### Slow Generation / Low TPS

- **Cause**: CPU thread counts exceeding physical cores (forcing hyperthreading overhead).
- **Resolution**: Ensure `LEO_THREADS=8` is set (do not use 12 logical threads, as virtual hyperthreads compete for shared L1/L2 caches).
