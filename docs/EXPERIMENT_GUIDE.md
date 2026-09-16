# HYPER-Ω Experimentation & Reproducibility Guide

## 1. Universal Reproduction Command
Any canonical HYPER-Ω experiment can be executed and independently verified with a single CLI invocation:

```powershell
python scripts/reproduce_experiment.py <WORKLOAD_ID>
```

### Supported Workload IDs:
1. **`HYPER_OMEGA_001`** (Dense Linear Algebra GEMM)
2. **`HYPER_OMEGA_GRAPHICS_001`** (Temporal Scene Reprojection & Color Clamping)
3. **`HYPER_OMEGA_LLM_001`** (Speculative Autoregressive Logit Step)
4. **`HYPER_OMEGA_SCIENCE_001`** (Toroidal Multigrid Heat Diffusion PDE)

---

## 2. Expected Output Format
Every experiment run reports:
1. Input and Output SHA-256 Hashes
2. Verification Verdict: `PASS`, `FAIL`, `UNKNOWN`, `INVALID`
3. Adversarial Falsification Verdict
4. Holdout Set Validation Verdict
5. Live Hardware Latency & Error Residuals
6. Cryptographic Certificate Hash

```
=======================================================
           REPRODUCIBILITY SUMMARY REPORT            
=======================================================
Workload ID:           HYPER_OMEGA_001
Overall Status:        VERIFIED
Verification Result:   PASS
Adversarial Result:    PASS
Holdout Result:        PASS
Candidate Latency:     2.308 ms
Input Hash:            1f7335b630e3a4e2...
Output Hash:           1a5fbc0b9e58b9d7...
Certificate Hash:      a2c9e209474fda8470cd464956f2dfb4e40bec472de44565ccf901482c66ae12
=======================================================

FINAL VERDICT: PASS
```

---

## 3. Running the Automated Test Suite
To verify all HYPER-Ω core modules and end-to-end pipelines:

```powershell
python -m pytest tests/test_hyper_omega_complete.py -v
python -m pytest tests/test_hyper_core_expanded.py -v
```
All tests are automated, deterministic, and execute without external network dependencies.
