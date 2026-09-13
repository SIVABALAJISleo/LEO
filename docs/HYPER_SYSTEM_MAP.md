# HYPER / LEO System Map & Architectural Topology

## 1. Executive Topology
HYPER / LEO is an **Adaptive Cheapest-Valid Computation Engine** designed to achieve application and contract parity on commodity heterogeneous hardware (specifically **Intel Core i5-12450H CPU + Intel UHD Graphics 48 EUs** with 16 GB Unified System RAM) without simulating external dedicated silicon.

```
                              [ INCOMING WORKLOAD ]
                                        │
                                        ▼
                         ┌─────────────────────────────┐
                         │      CONTRACT PARSER        │
                         │    (Exactness, SLA, Tol)    │
                         └──────────────┬──────────────┘
                                        │
                                        ▼
                         ┌─────────────────────────────┐
                         │ INFORMATION BOUNDARY ENGINE │
                         │ (Sufficient Statistic Map)  │
                         └──────────────┬──────────────┘
                                        │
                                        ▼
                         ┌─────────────────────────────┐
                         │   NECESSARY-WORK COMPILER   │
                         │ (Eliminable vs Needed Work) │
                         └──────────────┬──────────────┘
                                        │
                                        ▼
                         ┌─────────────────────────────┐
                         │    PATHWAY SEARCH ENGINE    │
                         │ (Reuse, Low-Rank, Sparsity) │
                         └──────────────┬──────────────┘
                                        │
                 ┌──────────────────────┴──────────────────────┐
                 ▼                                             ▼
       ┌───────────────────┐                         ┌───────────────────┐
       │   EXACT REUSE     │                         │  CANDIDATE SEARCH │
       │ (Cryptographic ID)│                         │ (Adaptive Kernel) │
       └─────────┬─────────┘                         └─────────┬─────────┘
                 │                                             │
                 └──────────────────────┬──────────────────────┘
                                        │
                                        ▼
                         ┌─────────────────────────────┐
                         │   FAIL-CLOSED VERIFIER      │
                         │ (Numerical, Adv, Holdout)   │
                         └──────────────┬──────────────┘
                                        │
                         ┌──────────────┴──────────────┐
                         ▼                             ▼
                      [ PASS ]                      [ FAIL ]
                         │                             │
                         ▼                             ▼
            ┌────────────────────────┐    ┌────────────────────────┐
            │   DECP & CERTIFICATE   │    │  SAFE EXACT FALLBACK   │
            │   (Evidence Ledger)    │    │ (Full Reference GEMM)  │
            └────────────────────────┘    └────────────────────────┘
```

---

## 2. Core Entry Points
- **Production CLI**: [`hyper_x/cli.py`](file:///c:/Users/sivab/OneDrive/Documents/HYPER/hyper_x/cli.py)
- **Authoritative Pipeline Runner**: [`hyper_x/pipeline.py`](file:///c:/Users/sivab/OneDrive/Documents/HYPER/hyper_x/pipeline.py)
- **System Doctor & Runtime Launcher**: [`leo.py`](file:///c:/Users/sivab/OneDrive/Documents/HYPER/leo.py)
- **Scorecard & Parity Dashboard**: [`hyper_x/dashboard.py`](file:///c:/Users/sivab/OneDrive/Documents/HYPER/hyper_x/dashboard.py)

---

## 3. Subsystem Breakdown
| Subsystem | Primary Path | Role & Operational Invariant |
| :--- | :--- | :--- |
| **Contract IR** | `hyper_x/contract_ir/` | Declares exactness class (`EXACT`, `NUMERICALLY_EQUIVALENT`, `PREDICTIVE`), numerical tolerance, latency SLO, and memory budget. |
| **Information Boundary** | `hyper_x/information_boundary/` | Partitions input data into `REQUIRED`, `OPTIONAL`, and `REDUNDANT` information relative to the observable. |
| **Necessary-Work** | `hyper_x/necessity/` | Quantifies original vs eliminable work; eliminates speculative assumptions from work reduction metrics. |
| **Pathway Search** | `hyper_x/pathway_search/` | Evaluates computational shortcuts: Exact Reuse > Reformulation > Low-Rank > Sparsity > Fallback. |
| **Authoritative Verifier**| `hyper_x/verification/` | Fail-closed multi-tier validation (Numerical $\epsilon$-bounds, adversarial stress, blind holdout). |
| **DECP** | `hyper_x/decp/` | Deterministic Exact-Compute & Parity Layer comparing physical output hashes and ULP distribution across hardware. |
| **Certificates** | `hyper_x/certificates/` | Emits cryptographically signed `execution_certificate.json` for every promoted pathway. |
| **Evidence Ledger** | `hyper_x/evidence/` | Records all measurements tagged with provenance (`MEASURED`, `REFERENCE`, `ESTIMATED`, `CACHED`). |
| **Heterogeneous Scheduler**| `universal_compute_router/` | Sub-100µs dispatch routing across P-cores, E-cores, and Intel UHD iGPU. |
| **Optimization Knowledge**| `hyper_x/knowledge/` | Stores verified transformations, empirical speedup factors, and falsification counterexamples. |
