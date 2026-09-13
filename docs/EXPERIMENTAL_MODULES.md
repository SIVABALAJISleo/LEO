# HYPER / LEO — Experimental & Quarantined Modules
**Document Version:** 2.0.0 (Ultra-Sonic Master Engineering)

---

## 1. Experimental Modules Quarantined from Production

The following research experiments exist in the repository but are strictly quarantined from the production execution path (`hyper_x/pipeline.py`) to prevent unverified claims:

| Module / Script | Domain | Research Hypothesis | Quarantine Reason |
| :--- | :--- | :--- | :--- |
| `leo_quantum_kan_lut_engine.py` | Representation | Lookup-table KAN basis replacement | Requires blind holdout validation across general distributions |
| `leo_fourier_light_transport.py` | Graphics | Synthetic Fourier basis light field transport | Evaluated on synthetic geometries only |
| `leo_prt_continuous_cache_experiment.py` | Graphics | Precomputed radiance transfer spherical harmonics | High memory footprint (> 2 GB) under 16 GB constraint |
| `algorithm_discovery/` | Search | Genetic algorithm mutation of matrix kernels | Unconstrained search space; requires formal e-graph saturation |
| `cbe/` | Legacy Engine | Initial Compute-Budget Elimination prototype | Superseded by `hyper_x/necessity/` and `hyper_x/pipeline.py` |
| `hyper_v2/`, `hyper_v3/` | Legacy Frameworks | Early iterations of HYPER engine | Preserved for historical test regression reference |

---

## 2. Policy for Experimental Promotion
An experimental module can ONLY be promoted to `ACTIVE_PRODUCTION` if:
1. It exposes a machine-readable `ContractIR`.
2. It undergoes adversarial testing against pathological inputs (NaN, Inf, noise).
3. It passes blind holdout verification with a documented generalization gap.
4. Its execution is candidate-coupled and generates an `ExecutionCertificate`.
5. It integrates into the deterministic fallback ladder.
