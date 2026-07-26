# COLIBRI / GLM-5.2 HARDWARE INTEGRATION GUIDE

This document outlines the strict hardware capabilities and instructions required to deploy the massive 744B Mixture-of-Experts (MoE) GLM-5.2 model using the **Colibrì C-Engine** in LEO AI.

---

## 1. Hardware Requirements

Running a 744B parameter model locally is extremely resource-intensive. Do **NOT** attempt to run Colibrì/GLM-5.2 on underpowered development laptops.

| Resource       | Minimum                    | Recommended                   | Notes                                                                                                               |
| -------------- | -------------------------- | ----------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| **System RAM** | 25 GB free                 | 32 GB+ total                  | Margin required for resident attention, embeddings, and context window.                                             |
| **Disk Space** | 400 GB free                | 900 GB+ (NVMe)                | FP8/int4 model weights take hundreds of GB. Must be on fast storage (e.g. ext4 NVMe), never on slow network mounts. |
| **CPU/GPU**    | 8+ cores (AVX2 / AVX-VNNI) | Intel UHD iGPU / Discrete GPU | Core threads used for active weight additions.                                                                      |

---

## 2. Installation & Weights Download

To set up and sanity test Colibrì:

1. **Clone and Compile the C-Engine:**
   ```bash
   git clone https://github.com/JustVugg/colibri
   cd colibri
   make glm ARCH=native
   ```
2. **Download Model Weights (GLM-5.2 FP8):**
   Use HuggingFace Hub snapshot download helper to pull model files (requires ~756 GB space during download):
   ```bash
   python3 tools/download_glm52.py
   ```
3. **Quantize the Model:**
   Generate the final `int4` quantized weights optimized for SSD streaming:
   ```bash
   ./coli convert --model /path/to/glm52_fp8 --out /path/to/glm52_i4
   ```
4. **Sanity Check Chat Mode:**
   ```bash
   ./coli chat --model /path/to/glm52_i4 --ram 24
   ```

---

## 3. Dynamic Router Logic & Fallbacks

To ensure smooth runtime operations, the LEO AI Router:

- **Capability Check:** Checks local system RAM and disk capacity on startup.
- **Smart Gateway Routing:** Simple tasks route to lightweight local Ollama (`qwen2.5:1.5b` or `phi3:mini`), leaving heavier reasoning requests to Colibrì.
- **Degradation Path:** If the hardware checklist fails or Colibrì's localhost gateway server (`http://localhost:8000`) is offline, LEO automatically routes all queries back to the lightweight Ollama instance, warning the user through UI alerts.
