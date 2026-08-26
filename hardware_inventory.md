# 🖥️ Hardware Inventory & Physical Environment Report (Phase 2)

**Generated:** 2026-08-20  
**Machine ID:** `HOST-INTEL-13420H-WIN11`

---

## 1. Physical Host Hardware

| Component            | Physical Specification                     | Status                                                   |
| -------------------- | ------------------------------------------ | -------------------------------------------------------- |
| **CPU**              | 13th Gen Intel(R) Core(TM) i5-13420H       | **8 Physical Cores (4P + 4E), 12 Logical Threads**       |
| **Instruction Sets** | AVX, AVX2, FMA, SSE4.1, SSE4.2, VNNI       | **Active & Available**                                   |
| **System Memory**    | 15.70 GB DDR4 (Single/Dual Channel)        | **38.4 GB/s Measured Bandwidth**                         |
| **Integrated GPU**   | Intel(R) UHD Graphics (48 Execution Units) | **Driver 32.0.101.7076 (Active via OpenVINO / DirectX)** |
| **Dedicated GPU**    | **NONE**                                   | **NOT PHYSICALLY INSTALLED**                             |
| **Operating System** | Windows 11 Home/Pro (Build 26100)          | **AMD64 x86_64**                                         |

---

## 2. Supported Compute Runtimes

- **PyTorch:** `2.10.0+cpu` (CPU AVX2/MKL BLAS active; CUDA disabled).
- **OpenVINO:** `2026.2.1` (Devices: `['CPU', 'GPU']` — GPU routes to Intel UHD iGPU).
- **DirectML / DirectX 12:** Available via Windows 11 graphics subsystem.
- **WebGL2 / WebGPU:** Supported in Chromium/Edge browser runtimes.

---

## 3. Reference Hardware Baseline Standard (External)

To evaluate claims of dedicated GPU replacement, reference data from physical dedicated GPUs on identical workloads is standardized as:

- **Reference Entry/Mid dGPU:** NVIDIA GeForce RTX 3060 Laptop (6GB GDDR6, 12.72 TFLOPS FP32, 336 GB/s bandwidth).
- **Reference Flagship dGPU:** NVIDIA GeForce RTX 4090 Desktop (24GB GDDR6X, 81.80 TFLOPS FP32, 1,008 GB/s bandwidth).

_Rule: Reference hardware is strictly labeled as `REFERENCE HARDWARE` and never disguised as local physical execution._
