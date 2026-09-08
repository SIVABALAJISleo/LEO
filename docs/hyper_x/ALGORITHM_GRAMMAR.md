# Compositional Algorithm Discovery Grammar (Phase 7)

## 1. Formal Grammar Specification

The HYPER-X Algorithm Discovery Grammar defines candidate algorithms not as monolithic opaque kernels, but as formal compositions of orthogonal mathematical operators.

### Extended Backus-Naur Form (EBNF)

```ebnf
Algorithm          ::= Pipeline
Pipeline           ::= Stage ('>>' Stage)*
Stage              ::= RepresentationStage 
                     | DecompositionStage 
                     | OrderingStage 
                     | KernelStage 
                     | CorrectionStage 
                     | VerificationStage

RepresentationStage ::= 'DENSE' | 'SPARSE_CSR' | 'FACTORED' | 'SPECTRAL_FFT' | 'Z_CURVE_TILED' | 'LOOKUP_TABLE'
DecompositionStage  ::= 'LOW_RANK_DECOMPOSE' | 'WAVELET_DECOMPOSE' | 'BLOCK_DECOMPOSE'
OrderingStage       ::= 'MORTON_REORDER' | 'HILBERT_REORDER' | 'CACHE_AWARE_TILE'
KernelStage         ::= 'MATMUL' | 'WINOGRAD_CONV' | 'FFT_CONV' | 'OUTPUT_PROJECT' | 'BITNET_LUT_DOT'
CorrectionStage     ::= 'RESIDUAL_CORRECTION' | 'BILATERAL_FILTER' | 'ERROR_BOUND_GUARD'
VerificationStage   ::= 'FREIVALDS_CHECK' | 'FROBENIUS_CHECK' | 'PERCEPTUAL_SSIM_CHECK'
```

---

## 2. Grammar Composition Operators

| Operator | Mathematical Transformation | Asymptotic Effect |
| :--- | :--- | :--- |
| `LOW_RANK` | $A \to U_r V_r$ via randomized SVD | Reduces $O(N^3)$ to $O(r N^2)$ |
| `SPARSE` | Prunes entries with $|A_{ij}| < \epsilon$ | Reduces operations to $O(\text{nnz} \cdot N)$ |
| `OUTPUT_PROJECT` | $(A B) x \to A (B x)$ | Reduces complexity from $O(N^3)$ to $O(N^2)$ |
| `TEMPORAL_DELTA` | $Y_t = Y_{t-1} + \Delta$ | Eliminates stationary pixel evaluations |
| `RESIDUAL_CORRECT`| $Y = Y_{\text{approx}} + R B$ | Guarantees contract tolerance satisfaction |
| `MORTON_REORDER` | Space-filling Z-curve memory tiling | Maximizes L1/L2 cache hit rate |

---

## 3. Evolutionary Search & Grammar Mutators

The Evolutionary Engine explores this grammar space using genetic operators:
1. **Operator Insertion**: Appends a correction stage (`RESIDUAL_CORRECTION`) to restore numerical precision when an aggressive low-rank decomposition fails verification.
2. **Operator Swap**: Substitutes dense matrix multiplication with sparse conditional execution when profiling detects high sparsity.
3. **Crossover**: Recombines representation choices from Candidate A with execution scheduling from Candidate B.
