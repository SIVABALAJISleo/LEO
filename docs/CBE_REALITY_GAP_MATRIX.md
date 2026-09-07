# LEO CBE — Repository Reality-Gap Matrix

**Date of Audit**: September 2026  
**Auditor**: Principal Architect & Senior Graphics/Intel-Optimization Team  
**Physical Target**: Intel Core i5-13420H (4P+4E cores, 12 threads), Intel UHD Graphics iGPU (48 EUs, Gen12 Xe-LP), Windows 11  
**Status Rule**: Never designate simulated or mock functionality as physical hardware acceleration.

---

## 1. Classification Taxonomy

- **REAL**: Genuine, functional implementation executing actual mathematical calculations or hardware operations without synthetic shortcuts.
- **PARTIAL**: Substantive implementation containing genuine logic, but relying on stubs, placeholders, or partial loops for certain stages.
- **SIMULATED**: Mathematical calculation or execution flow is modeled in CPU/NumPy software rather than dispatched to the intended hardware target.
- **MOCK**: Hardcoded return values, synthetic latencies, or randomized fake training data masquerading as real algorithmic output.
- **CLAIM_ONLY**: Architectural documentation, docstrings, or method names claiming capabilities not supported by runnable code.
- **UNUSED**: Valid code or shader files present in the repository that are never loaded, compiled, or referenced by any active runtime path.
- **BROKEN**: Code containing syntax errors, SIMD type mismatches, out-of-bounds memory writes, or fatal logic bugs.
- **DUPLICATE**: Redundant re-implementations of functionality already provided elsewhere in the repository.
- **MISSING**: Necessary architectural components specified in system design but completely absent from the codebase.

---

## 2. Exhaustive Reality-Gap Matrix

| Component / File Path | Classification | Detailed Evidence / Line Inspection | Remediation in CBE |
| :--- | :--- | :--- | :--- |
| `core_ai/bitnet_engine.py` | **PARTIAL / SIMULATED** | Weights are quantized via `torch.round(param / scale)` to `{-1, 0, 1}`, but `_optimize_for_cpu` simply sets `'avx2_optimized': True` in a dictionary with no native kernel invocation. `_save_model` calls `torch.save` rather than true GGUF/INT8 packaging. | Integrate genuine INT8/ternary packing and benchmark memory bandwidth reduction. |
| `core_ai/speculative_engine.py` | **SIMULATED / MOCK** | Lines 86–88: Hardcodes `accepted_len = min(6, max_new_tokens - tokens_produced)` with a comment "Simulate high target acceptance". Never performs statistical rejection sampling or token verification against the target model. | Replace hardcoded token acceptance with true probability verification and draft acceptance tracking. |
| `core_ai/heterogeneous_orchestrator.py` | **SIMULATED / MOCK** | Lines 216–224: When OpenVINO GPU is not loaded, hardcodes `cpu_time = 24.5`, `gpu_time = 38.2`, `hetero_time = 9.8`, `singularity_time = hetero_time * 0.15`. `AVX2VNNIOrchestratorKernel` is an `np.dot` with random weights. | Replaced by `cbe/scheduling/execution_scheduler.py` and real OpenVINO GPU dispatch. |
| `core_ai/semantic_cache.py` | **REAL** | Real SHA-256 exact matching, normalized n-gram and FAISS vector cosine similarity fallback, and graph-based substring matching. | Preserved and integrated into `cbe/controller/cbe_controller.py` as Tier 0 / Tier 1 cache. |
| `core_ai/moe_architecture.py` | **REAL** | Genuine PyTorch implementation of Top-K gating router and sparse expert evaluation activating only Top-2 experts per token. | Retained as sparse cognitive execution path. |
| `bypass/leo_irrelevance_engine.py` | **PARTIAL / MOCK** | Chains temporal, hash gate, and early exit, but `_execute_base_model` returns a hardcoded mock bounding box `np.array([100, 100, 200, 200, 0.95])`. | Hooked to real base render and inference pipelines. |
| `bypass/leo_temporal_diffing.py` | **MOCK / CLAIM_ONLY** | Subsamples every 100th pixel (`[::100, ::100]`). If diff < 5%, returns `previous_output * 0.99 + 0.01` as a "mock transpose/shift". No motion vectors, depth, or disocclusion handling. | Completely upgraded to `cbe/reuse/temporal_reuse.py` with motion-compensated reprojection. |
| `bypass/leo_early_exit_router.py` | **MOCK** | Trains a `DecisionTreeClassifier` on random Gaussian noise (`np.random.randn(100, 256)`) with random labels (`np.random.randint(0, 2, 100)`). Multiplies state by `2.5` as "mock extrapolation". | Replaced by calibrated confidence and entropy thresholding over real intermediate activations. |
| `render/fsr_upscaler.py` | **MOCK / SIMULATED** | Line 25: Simply executes `np.repeat(np.repeat(low_res_frame, 2, axis=0), 2, axis=1)`. Nearest-neighbor pixel repetition labeled as "FSR 2/3". | Upgraded to true Edge-Adaptive Spatial Sharpening and temporal accumulation in `cbe/reconstruction/`. |
| `render/multi_fidelity_renderer.py` | **MOCK / CLAIM_ONLY** | Lines 29–48: Returns hardcoded `latency_ms: 0.5`, `fps: 2000.0`, `ssim: 1.0` for Tier 1, and `(time - t0) * 1000 + 15.0`, `fps: 60.0`, `ssim: 0.985` for Tier 2. | Fully upgraded into 8-tier hierarchy in `cbe/` with true timing, ray counting, and SSIM measurement. |
| `render/software_rt_pipeline.py` | **MOCK** | Line 39: Generates `noisy_buffer = np.random.uniform(0.1, 0.9, ...)` instead of tracing rays. Claims `effective_spp_quality: 100` and `actual_rays_fired_pct: 4.0`. | Upgraded to real sparse ray tracing steered by the CBE importance map. |
| `render/rendering_contract.py` | **REAL** | Genuine 3D sphere ray casting (`_trace_scene`), sub-pixel jitter AA, edge-preserving bilateral filtering, and mathematically exact SSIM/PSNR calculation. | Preserved and integrated as ground-truth verification reference. |
| `render/oidn_denoiser.py` | **PARTIAL / BROKEN** | Line 40: Denoising loop truncates at `for x in range(min(w, 64))`, leaving the entire remainder of the frame un-denoised. | Replaced by full bilateral and Intel OpenVINO neural denoiser. |
| `universal_compute_router/intel_optimal_execution.py` | **SIMULATED** | Claims OpenVINO kernel fusion (MatMul + Add + LayerNorm) on iGPU, but lines 55–60 execute `np.dot(x, W) + b` in NumPy on the host CPU. | Replaced by real OpenVINO GPU compilation targeting the Intel UHD Graphics iGPU (`GPU.0`). |
| `universal_compute_router/orchestrator.py` | **MOCK** | Video, data, and solver execution methods return static mock strings like `"[VIDEO_ENGINE] Processing request with FFmpeg/ONNX"`. | Routed to genuine execution backends or clean procedural handlers. |
| `universal_compute_router/router_logic.py` | **PARTIAL** | Real UCB / epsilon-greedy bandit algorithm and exponential moving average score updates, but was routing to mocked engine methods. | Upgraded in `cbe/controller/workload_controller.py` with real backend routes and safety contracts. |
| `real_hardware_benchmark.py` | **REAL** | Genuine FP32 GEMM benchmark executing across CPU single-thread, PyTorch multi-thread, and physical Intel UHD iGPU via OpenVINO Core. | Maintained as core hardware verification baseline. |
| `real_cognitive_benchmark.py` | **PARTIAL** | Runs live queries through `LeoEngine`, but underlying pipeline included simulated token acceptance and mock intermediate layers. | Connected to real verified CBE components. |
| `kernels/fused_kernels.cpp` | **BROKEN** | AVX2 kernel contains fatal bugs: `_mm256_add_epi32` applied to 8-bit masks, and vector store `_mm256_storeu_ps` overwriting adjacent elements because scalar loop `j` increments by 1 instead of 8. | Documented and fixed; provided OpenVINO GPU and clean C++ reference implementations. |
| `kernels/igpu_opencl/binary_xor.cl` | **UNUSED** | Valid OpenCL C kernel implementing binary XNOR and popcount bit-twiddling, but never compiled or called anywhere in the repository. | Integrated into OpenCL execution tests. |
| `kernels/sycl/leo_custom_sycl.cpp` | **CLAIM_ONLY / UNUSED** | DPC++/SYCL source code exists, but no build system or compiled `.pyd`/`.so` library exists; host lacks the proprietary Intel oneAPI DPC++ compiler toolchain. | Kept as reference research; production path uses OpenVINO GPU. |
| `kernels/directml/dml_backend.py` | **SIMULATED** | Falls back to `return np.dot(a, b)` with a shim. | Replaced by real Intel OpenVINO backend. |
| `kernels/webgpu/leo_compute.wgsl` | **UNUSED** | Valid WGSL compute shader for matrix multiplication, but never bound or dispatched by any Python WebGPU runtime. | Kept as web/browser reference. |
| `predictors/predictive_reality.py` | **MOCK** | Generates random variation outcomes with `round(random.uniform(0.90, 0.99), 3)` probabilities. | Replaced by `cbe/prediction/` utilizing Kalman and linear state trajectory extrapolation. |
| `predictors/state_engine.py` | **PARTIAL** | Basic constant-velocity kinematic extrapolation and LERP reconciliation. | Extended into full 6-DOF camera and object state predictor. |
| `optimization/leo_alchemy.py` | **SIMULATED** | Prints a string containing simulated OpenVINO NNCF code (`"print('[Alchemy] Step 2 & 3 Simulation...')"`). | Replaced with real model conversion and precision selection. |

---

## 3. Remediation Strategy Summary

1. **Zero Mocks in Production Paths**: Every mock return, hardcoded FPS (e.g. `fps=2000`), hardcoded latency (`latency=0.5`), and random training loop is completely removed from active pipelines.
2. **Physical Intel iGPU Execution**: OpenVINO is used as the primary production backend for Intel UHD Graphics (`GPU.0`), compiling genuine computation graphs for neural reconstruction, tensor operations, and inference.
3. **True Mathematical Baselines**: All compute elimination numbers are measured against real unaccelerated ground-truth execution (e.g., 64 SPP Monte Carlo ray tracing, full FP32 GEMM), with zero double-counting.
