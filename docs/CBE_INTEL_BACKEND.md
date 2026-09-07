# LEO CBE — Intel Backend & Hardware Optimization Specification

## 1. Hardware Architecture: Intel Core i5-13420H & Intel UHD Graphics

The Compute-Budget Elimination Engine is tailored for Intel Gen12 Xe-LP integrated graphics paired with Raptor Lake hybrid multi-core CPU architecture.

### 1.1 CPU Topology (Hybrid P+E Cores)
- **4 Performance Cores (P-Cores, Golden Cove)**: 2 threads per core (8 logical threads), up to 4.6 GHz Max Turbo. Assigned to latency-critical stage coordination, DAG traversal, and high-frequency state diffing.
- **4 Efficient Cores (E-Cores, Gracemont)**: 1 thread per core (4 logical threads), up to 3.4 GHz. Assigned to background radiance cache maintenance, spatial hash indexing, and asynchronous logging.
- **Instruction Extensions**: AVX2 (256-bit SIMD) and Intel Deep Learning Boost (VNNI / DP4A) for INT8 matrix multiply accumulation.

### 1.2 Intel UHD Graphics (Xe-LP Architecture)
- **48 Execution Units (EUs)**: Organized into sub-slices capable of FP32, FP16, and INT8 operations.
- **Unified Shared Memory (USM)**: Integrated graphics shares physical system RAM with the CPU, allowing true zero-copy pointer transfers via OpenCL/Level Zero USM buffers without PCIe bus serialization.
- **Variable Rate Shading (VRS Tier 1)**: Native per-draw and coarse shading rate support.

---

## 2. OpenVINO Integration & Model Optimization

### 2.1 Dynamic Spatial Shapes & Compilation
OpenVINO by default compiles models with static input shapes. To support continuous adaptive resolution scaling ($33\%$ to $100\%$ scale ladders), the model is compiled with dynamic dimensions:

```python
import openvino as ov
core = ov.Core()
model = core.read_model("models/tiny_intel_recon.onnx")
# Dynamic batch and spatial dimensions: [-1, 8, -1, -1]
model.reshape([-1, 8, -1, -1])
compiled_model = core.compile_model(model, "GPU", {"PERFORMANCE_HINT": "LATENCY"})
```

### 2.2 Cold-Start Mitigation (Warmup Iteration)
The first inference pass on the Intel GPU plugin compiles OpenCL shader programs, creating a 50-100ms cold start spike. CBE executes an explicit dummy forward pass during initialization:

```python
# Initialization warmup ensures zero JIT shader stalls during active rendering
dummy = np.zeros((1, 8, 32, 32), dtype=np.float32)
_ = compiled_model([dummy])
```

### 2.3 Kernel Fusion
Matrix multiplication, bias addition, and LayerNorm operations are fused into single OpenVINO execution subgraphs, eliminating round-trip DRAM memory bandwidth bottlenecks:

$$\mathbf{y}_{\text{norm}} = \text{LayerNorm}(\mathbf{x} \mathbf{W} + \mathbf{b})$$
