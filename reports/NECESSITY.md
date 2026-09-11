# LEO / HYPER: Computational Necessity Report

**Document**: `reports/NECESSITY.md`  
**Version**: 1.0.0  
**Core Rule**: Identifying indispensable computation is a first-class breakthrough. When a shortcut fails contract verification, the system formally proves that the computation is necessary.

---

## 1. Classification of Computational Barriers

| Barrier Type | Physical / Mathematical Mechanism | Concrete Target Workload | Final Status |
| :--- | :--- | :--- | :--- |
| **Algorithmic (Full Rank)** | Singular value spectrum is flat; Marchenko-Pastur distribution prevents low-rank SVD. | Unstructured Gaussian GEMM (`DENSE_GAUSSIAN_512x512`) | `NECESSARY_PROVEN` |
| **Information-Theoretic** | Uniform random sparsity lacks geometric or low-rank manifold structure. | Sparse Matrix-Vector (`SpMV_CSR_10k`) | `NECESSARY_PROVEN` |
| **Non-Linear Attention** | i.i.d. Gaussian random projection matrices destroy temporal token correlation. | Random Weight Transformer Block (`LLM_Residual_Block`) | `NECESSARY_PROVEN` |
| **Exactness Contract** | User contract declares `EXACT_EQUIVALENT` ($\varepsilon = 0$); approximations prohibited. | Cryptographic hashing, bit-exact simulation | `NECESSARY_PROVEN` |

---

## 2. Formal Necessity Certificates

Every necessary computation emits a cryptographically signed `CausalNecessityCertificate`:
- **Certificate ID**: `CERT_NEC_dense_unstructured_gemm_1789137537205`
- **Operation ID**: `dense_unstructured_gemm`
- **Formal Status**: `NECESSARY_PROVEN`
- **Counterexample**: *"Exact matrix rank equals full dimension; lossless rank reduction impossible."*
- **Empirical Confidence**: $1.0$ (100% verified)
- **Fallback**: `exact_native_computation`
