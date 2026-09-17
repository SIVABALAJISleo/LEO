# HYPER v8 System Architecture

## 1. Overview
HYPER v8 is a **Necessary-Work Compiler (NWC)** and **Contract Parity Engine** designed for local heterogeneous execution on the target hardware:
- **CPU**: Intel Core i5-12450H (4 P-cores + 4 E-cores, 12MB L3 Smart Cache)
- **iGPU**: Intel UHD Graphics (48 Execution Units, unified system memory)
- **RAM**: 16 GB DDR5/LPDDR5
- **OS**: Windows 11
- **Constraint**: Strict software-only optimization. Zero dedicated GPU (dGPU), zero cloud offload.

HYPER v8 replaces blind recomputation with contract-bounded computation elimination:
$$\mathcal{W}_{\text{eliminated}} = \mathcal{W}_{\text{total}} - \mathcal{W}_{\text{necessary}}$$

```
                +----------------------------+
                |     ComputeContractV2      |
                +--------------+-------------+
                               |
                               v
                +----------------------------+
                |  CheapestValidPathSelector  |
                +--------------+-------------+
                               |
       +-----------------------+-----------------------+
       |                       |                       |
       v                       v                       v
[Exact Cache]         [Exact Residual]        [Sparse / Low-Rank]
(SHA-256 Lookup)      (Delta Decomposition)    (CSR / Truncated SVD)
       |                       |                       |
       +-----------------------+-----------------------+
                               |
                               v
                +----------------------------+
                |     ContractValidator      |
                +--------------+-------------+
                               |
                 [Pass] +------+------+ [Fail]
                        |             |
                        v             v
             ExecutionCertificate    Fallback Path (Reference BLAS)
```

---

## 2. Core Subsystems

### 2.1 Necessary-Work Compiler (NWC)
The NWC (`hyper.v8.nwc`) models computational pipelines as directed acyclic graphs (DAGs) using `NecessaryWorkGraph`.
- **Node Classification**: Nodes are assigned `NecessityLabel` values (`REQUIRED`, `REUSABLE`, `ELIMINABLE`, `REDUCIBLE`, `APPROXIMABLE`, `ZERO_WORK`).
- **Dependency Tracking**: `DependencyAnalyzer` determines causal cones of influence for operations like GEMM:
  $$C[i, :] = A[i, :] \times B$$
  If row $i$ of $A$ is unchanged and $B$ is unchanged, $C[i, :]$ is identical and requires 0 FLOPs.
- **Change Detection**: `ChangeDetectionEngine` computes cryptographic hashes and identifies sparse row/column deltas.

### 2.2 Exact Residual Engine
Located in `hyper.v8.residual`:
- Decomposes updates:
  $$C_{t} = A_{t} B_{t} = (A_0 + \Delta A)(B_0 + \Delta B) = A_0 B_0 + \Delta A B_0 + A_0 \Delta B + \Delta A \Delta B$$
- If only $k$ rows of $A$ change, the complexity drops from $2MNK$ to $2kNK$, eliminating $(1 - k/M) \times 100\%$ of work with exact mathematical equivalence (`max_abs_error = 0.0`).

### 2.3 Heterogeneous Scheduler V2
Located in `hyper.v8.scheduler`:
- Probes hardware via `probe_hardware()` and issues an unforgeable `DeviceCertificate`.
- Partitions large matrix workloads across CPU (AVX2 multi-threaded BLAS) and Intel UHD iGPU (OpenCL Zero-Copy UVA).
- Strictly verifies whether offload improves performance before committing to GPU dispatch.

### 2.4 Self-Falsification Engine
Located in `hyper.v8.falsification`:
- Executes 12 adversarial test cases: random dense full-rank, identity, pathological sparsity, ill-conditioned matrices, extreme dynamic ranges, NaN/Inf injection, cache collision attacks, high-frequency alternating signs, rank-1 updates, and epsilon perturbations.
- Guarantees fail-safe fallback without silent corruption.
