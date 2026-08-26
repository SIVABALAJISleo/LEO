# 🔁 HYPER Full-Stack Falsification Reproduction Guide

To independently reproduce the empirical findings of this Full-Stack GPU Replacement Falsification Campaign on any Windows or Linux workstation:

---

## 1. Prerequisites

- Python 3.10+
- PyTorch (`pip install torch`)
- OpenVINO (`pip install openvino`)
- NumPy & psutil (`pip install numpy psutil`)

---

## 2. One-Command Full-Stack Reproduction

Execute the full adversarial gauntlet:

```bash
python full_stack_falsification_suite.py
```

This will:

1. Probe local physical hardware (CPU cores, iGPU EUs, RAM bandwidth).
2. Execute real physical computations across all 8 domains (Compute, AI, Graphics, Ray Tracing, Media, Scientific, Applications).
3. Validate numerical isomorphism and output error deltas.
4. Compare local measurements against established dedicated GPU baselines (RTX 3060 / RTX 4090).
5. Output `FULL_STACK_RESULTS.json` and `FULL_STACK_RESULTS.csv`.

---

## 3. Individual Component Benchmarks

To run the real physical FP32 GEMM negative control:

```bash
python real_hardware_benchmark.py
```

To run the real cognitive interactive AI benchmark (50 prompts):

```bash
python real_cognitive_benchmark.py
```

To view the browser-based simulation suite:
Open `academic_demonstration_suite.html` or `falsification_suite.html` in any Chromium/Edge browser.
