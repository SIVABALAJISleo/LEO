#include <immintrin.h>
#include <stdint.h>

#ifdef _WIN32
#define EXPORT __declspec(dllexport)
#else
#define EXPORT
#endif

extern "C" {

/**
 * Production-grade AVX2 Ternary Matrix Multiplication (Zero-Multiplication Add/Subtract)
 * Designed for INT8 activations and Ternary {-1, 0, +1} weights.
 *
 * M: Number of rows in activations
 * N: Number of columns in weights (output features)
 * K: Number of columns in activations / rows in weights (reduction dim)
 *
 * activations: M x K matrix (int8_t)
 * ternary_weights: K x N matrix (int8_t) — stored with elements: -1, 0, +1
 * output: M x N matrix (int32_t)
 *
 * Optimizations:
 * - AVX2 SIMD vectorization (processing 32 elements per iteration).
 * - Cache-blocking across K dimension to fit in L1/L2 Cache.
 */
EXPORT void ternary_matmul_avx2(
    int M, int N, int K,
    const int8_t* __restrict activations,
    const int8_t* __restrict ternary_weights,
    int32_t* __restrict output
) {
    // Zero out output buffer
    for (int i = 0; i < M * N; ++i) {
        output[i] = 0;
    }

    // Cache-blocking parameters (tuned for L2 size)
    const int BLOCK_K = 256;
    const int BLOCK_N = 64;

    // Load constant registers
    __m256i v_one = _mm256_set1_epi8(1);
    __m256i v_neg_one = _mm256_set1_epi8(-1);
    __m256i v_zero = _mm256_setzero_si256();

    for (int kk = 0; kk < K; kk += BLOCK_K) {
        int k_end = (kk + BLOCK_K < K) ? (kk + BLOCK_K) : K;
        for (int nn = 0; nn < N; nn += BLOCK_N) {
            int n_end = (nn + BLOCK_N < N) ? (nn + BLOCK_N) : N;

            for (int i = 0; i < M; ++i) {
                for (int k = kk; k < k_end; ++k) {
                    // Load activation element and broadcast across vector
                    int8_t act_val = activations[i * K + k];
                    if (act_val == 0) continue; // Skip compute for sparse activations
                    
                    __m256i v_act = _mm256_set1_epi8(act_val);

                    // Vectorized N-loop
                    for (int j = nn; j < n_end; j += 32) {
                        // Load 32 ternary weights
                        __m256i v_weight = _mm256_loadu_si256((const __m256i*)(ternary_weights + k * N + j));

                        // Create mask for positive (+1) and negative (-1) weights
                        __m256i mask_pos = _mm256_cmpeq_epi8(v_weight, v_one);
                        __m256i mask_neg = _mm256_cmpeq_epi8(v_weight, v_neg_one);

                        // Accumulate additions and subtractions conditionally via blendv
                        __m256i v_add = _mm256_blendv_epi8(v_zero, v_act, mask_pos);
                        __m256i v_sub = _mm256_blendv_epi8(v_zero, v_act, mask_neg);

                        // Convert INT8 additions to INT32 and accumulate in output
                        // For simplicity, directly add to the output matrix in scalar-mapped slices
                        alignas(32) int8_t raw_add[32];
                        alignas(32) int8_t raw_sub[32];
                        _mm256_storeu_si256((__m256i*)raw_add, v_add);
                        _mm256_storeu_si256((__m256i*)raw_sub, v_sub);

                        for (int v = 0; v < 32 && (j + v) < n_end; ++v) {
                            output[i * N + (j + v)] += (int32_t)raw_add[v] - (int32_t)raw_sub[v];
                        }
                    }
                }
            }
        }
    }
}

}
