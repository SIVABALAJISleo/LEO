# Known Limitations & Hardware Boundaries

## 1. Physical Hardware Non-Equivalence

1. **Integrated GPU Bandwidth:** The host Intel UHD Graphics shares physical DDR system memory bandwidth with the CPU (measured ~18.57 GB/s). Dedicated GPUs (e.g. RTX 4090 with >1000 GB/s GDDR6X) possess approximately $50\times$ higher raw memory bandwidth. No software transformation can alter this physical bus capacity.
2. **Dense FP32 ALU Saturation:** For purely compute-bound, dense, non-sparse matrix multiplications that do not fit into cache, an integrated GPU cannot match the raw TFLOPs of a dedicated 450W accelerator.
3. **Discrete Driver Availability:** If Intel OpenCL or Vulkan drivers are uninstalled or corrupted in the host Windows environment, execution gracefully falls back to CPU AVX2.

---

## 2. Algorithmic Precondition Boundaries

1. **Sparsity Thresholds:** Sparse CSR execution provides genuine speedups only when zero fraction $\ge 80\%$. On dense matrices, sparse index lookup incurs severe indirection overhead.
2. **Convolution Dimensions:** FFT fast convolution is advantageous only when the kernel length $M \ge 64$ and signal length $N \ge 512$. For tiny $3\times 3$ spatial kernels, direct convolution or Winograd is faster due to FFT transform overhead.
3. **Quantization Precision Loss:** Symmetric INT8 quantization reduces memory footprint by $4\times$, but introduces quantization noise ($\text{RMSE} \approx 0.005$). It cannot be awarded `BITWISE_EXACT` or `NUMERICALLY_EQUIVALENT` status.

---

## 3. Python Interpreter Overhead

When implementing numerical algorithms in pure Python loops rather than compiled C/C++/AVX2 kernels (e.g. SciPy or NumPy BLAS), Python bytecode interpretation overhead dominates. All production performance pathways must compile or vectorize into C-extensions or NumPy C-buffers to achieve true latency improvements.
