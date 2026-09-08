# Hardware Advantage Erasure & Decoupled Metrics

## 1. The Asymmetric Architectural Thesis

A dedicated discrete GPU (e.g. NVIDIA H100 / RTX 4090) maintains raw hardware superiority over a low-power CPU + integrated GPU in three primary dimensions:
1. **Raw Dense Compute Density**: Thousands of Tensor Cores capable of hundreds of TFLOPs of dense matrix multiplication.
2. **Dedicated Memory Bandwidth**: High-bandwidth memory (HBM3 / GDDR6X) operating at 1.5 to 3.3 TB/s.
3. **Interconnect & Staging Bandwidth**: NVLink / PCIe Gen5 lanes.

However, an integrated architecture (Intel 13th Gen Core i5-13420H + Intel UHD Graphics 48 EUs) possesses unique structural properties:
1. **Zero-Copy Shared System Memory**: CPU and integrated GPU share the identical physical LPDDR5/DDR5 address space. Tensors can be manipulated across CPU and iGPU without PCIe serialization, host-to-device transfers, or DMA marshalling.
2. **Algorithmic Information Boundary Neutralization**:
   - If an algorithm eliminates 70% to 90% of the mathematical operations required by a task, the brute-force FLOP advantage of Tensor Cores is mathematically neutralized.
   - Example: A GPU running an $O(N^3)$ dense kernel at 100 TFLOPs requires time $T = N^3 / 10^{14}$. An integrated CPU running a wormhole algorithm in $O(r N^2)$ at 1 TFLOP requires time $T = 2 r N^2 / 10^{12}$. When $N = 4096$ and rank $r = 16$, the wormhole pathway requires $1300\times$ fewer operations, achieving lower latency and energy consumption on commodity hardware.

---

## 2. Decoupled Metric Definitions

To ensure scientific honesty and prevent confusion between mathematical pruning and raw silicon speed, HYPER-X enforces decoupled metrics:

1. **`WORK_ELIMINATION`**:
   $$\text{WorkElimination} = 1.0 - \frac{\text{Necessary FLOPs}}{\text{Nominal Dense FLOPs}}$$
   Measures the fraction of algorithmic work rendered unnecessary by the contract.
2. **`RAW_HARDWARE_SPEEDUP`**:
   $$\text{Speedup} = \frac{\text{Measured Reference Latency (ms)}}{\text{Measured Candidate Latency (ms)}}$$
   Strict wall-clock ratio on the identical physical machine, including all runtime overheads.
3. **`NUMERICAL_PARITY`**:
   $$\text{RelError} = \frac{\|C_{\text{ref}} - C_{\text{cand}}\|_F}{\|C_{\text{ref}}\|_F + 10^{-8}}$$
   Must be less than or equal to $\epsilon_{\text{contract}}$.
4. **`GPU_ADVANTAGE_ERASED`**:
   Weighted percentage of Tensor Core, HBM, and interconnect advantage neutralized by the specific transformations applied.
