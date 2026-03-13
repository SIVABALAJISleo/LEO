# HV Engine: High-Velocity CPU Architecture

## Integration Flow Diagram

```text
[Input Sources] 
      │
      ▼
[Physics Engine (240Hz)] ───► [Deterministic Replay Buffer]
      │                              │
      ▼                              ▼
[BVH Spatial Index] <───► [Particle System (Culling)]
      │                              │
      ▼                              ▼
[Hybrid Rasterizer] <───► [Voxel Radiance Grid (Baked)]
      │                              │
      ▼                              ▼
[Camera Streams] ────► [Vision Pipeline (Temporal Smoothing)]
      │                              │
      ▼                              ▼
[Final Perceptual Output (60Hz)] <── [Optical Flow Interpolation]
```

## Performance Rationale: Why this avoids GPU

### 1. Rendering: Baked Sparse Voxels
- **GPU Way**: Real-time ray-tracing (BVH traversal + intersection + shading).
- **HV Way**: **Offline NeRF baking** into NanoVDB-style grids. Sparse voxels store pre-integrated lighting.
- **Why it works**: A ray lookup becomes a single O(1) array access. CPU caches (L1/L2) are extremely efficient at this. Interpolation is handled via SIMD.

### 2. Physics: Fixed-Point BVH
- **GPU Way**: Massive parallel GPGPU solver.
- **HV Way**: **Fixed-point arithmetic** + **O(logN) BVH**. 
- **Why it works**: By reducing $O(N^2)$ brute-force collisions to $O(N \log N)$ via BVH, the CPU can handle complex scenes at 240Hz. Fixed-point eliminates floating-point drift, ensuring perfect determinism for replay.

### 3. Vision: Temporal Coherence
- **GPU Way**: Inference on every frame.
- **HV Way**: **Frame Skipping** + **Optical Flow Warp**.
- **Why it works**: Processing only 25% of frames (every 4th) reduces total compute by 75%. Optical flow (using RAFT on ONNX Runtime with SIMD) "fills the gaps" cheaply, providing a 60 FPS perceptual output.

### 4. Particles: Seeded RNG
- **GPU Way**: 10M live particle buffers updated on GPU.
- **HV Way**: **Procedural trajectories**. 
- **Why it works**: Particles aren't "stored"; they are "computed" on-the-fly from a seed and time variable. Spatial grid culling ensures only the 1% visible particles are even generated.

### 5. ML: INT8 SIMD
- **GPU Way**: Raw FP16/FP32 TFLOPS.
- **HV Way**: **INT8 Quantization** + **AVX-512 Vectorization**.
- **Why it works**: Modern CPUs (i5/Ryzen) have massive throughput for integer math (VNNI, AVX). Quantized models are cache-local, reducing memory bandwidth bottlenecks.
