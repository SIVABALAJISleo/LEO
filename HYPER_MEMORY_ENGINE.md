# HYPER Memory & Dataflow Engine

## 1. Memory as Primary Cost
On the i5-12450H, system memory bandwidth is physically bounded to **51.2 GB/s**. By contrast, an NVIDIA RTX 4090 possesses **1,008 GB/s** (20x higher). Consequently, algorithmic optimization on commodity laptop silicon must treat memory movement as the primary bottleneck:

$$\text{Time} \approx \max\left( \frac{\text{FLOPs}}{\text{Peak GFLOPS}}, \frac{\text{Bytes Read} + \text{Bytes Written}}{\text{Memory Bandwidth (51.2 GB/s)}} \right)$$

---

## 2. Memory-First Optimization Strategies

1. **L1/L2/L3 Cache Alignment & Tiling**: Tile matrix dimensions to match CPU L1 Data Cache (48 KB per P-core) and L2 Cache (1.25 MB per P-core).
2. **Structure of Arrays (SoA) vs Array of Structures (AoS)**: Automatically transposes particle, geometry, and feature buffers into contiguous SoA format to maximize 256-bit AVX2 SIMD utilization.
3. **Buffer Reuse & Memory Pools**: Pre-allocates a 256 MB circular ring buffer (`AlchemySharedMemoryBuffer`), recycling intermediate buffers to eliminate heap allocation (`malloc`/`free`) overhead and OS page fault latency.
4. **Kernel Fusion**: Fuses elementwise activations (ReLU, GELU, BiasAdd) directly into register accumulation loops, preventing roundtrips to system RAM.
