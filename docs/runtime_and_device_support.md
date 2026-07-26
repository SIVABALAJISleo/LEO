# LEO AI v∞ Runtime and Device Support Matrix

LEO AI v∞ is designed to execute local inference using high-efficiency CPU, integrated GPU (iGPU), and Neural Processing Unit (NPU) runtimes.

---

## 1. Supported Devices & Backends

### CPU Backend

- **Instruction Sets**: AVX2, AVX-512, AMX (Intel 4th-Gen Xeon & Core Ultra).
- **Execution Profile**: Low latency, high compatibility.
- **Optimization Strategy**: Work-stealing thread mapping pinned to physical cores to maximize L1/L2 cache locality.

### iGPU Backend

- **Runtime Bindings**: Vulkan (via `llama.cpp` Vulkan backend), OpenCL/DirectML (via `OpenVINO`).
- **Optimization Strategy**: Fused matrix multiplications and sparse activation clamping.

### NPU Backend

- **Runtime Bindings**: DirectML (Windows NPU API), OpenVINO NPU plugin.
- **Optimization Strategy**: Minimum power footprint. Recommended for small background classification tasks.

---

## 2. Environment Configuration Tuning

You can force execution overrides using these environment variables before running LEO:

| Variable             | Values                          | Description                               |
| :------------------- | :------------------------------ | :---------------------------------------- |
| `LEO_DEVICE`         | `auto`, `cpu`, `igpu`           | Target device selection override.         |
| `LEO_RUNTIME`        | `auto`, `openvino`, `llama_cpp` | ML engine backend executor selection.     |
| `LEO_THREADS`        | Integer (e.g. `8`)              | CPU computation thread pool bounds.       |
| `LEO_PREFIX_CACHING` | `1`, `0`                        | Enable prompt prefix KV-cache reuse.      |
| `LEO_SPECULATIVE`    | `1`, `0`                        | Enable speculative verification decoding. |
