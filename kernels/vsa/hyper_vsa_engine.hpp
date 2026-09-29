/**
 * PROJECT LEO / HYPER: C++ NATIVE ACCELERATION BACKEND
 * FILE: kernels/vsa/hyper_vsa_engine.hpp
 * 
 * Vector Symbolic Architecture (VSA) Bitwise Surrogate Engine
 * Designed strictly for Intel Core i5-12450H (AVX2, Golden Cove P-Cores).
 * 
 * Eliminates dense FP32 matrix multiplications via:
 * 1. Hyperdimensional binary projection (R^d -> {0,1}^D).
 * 2. 256-bit SIMD bitwise XOR (_mm256_xor_si256).
 * 3. In-register AVX2 parallel PSHUFB 4-bit LUT population count.
 */

#pragma once

#ifndef HYPER_VSA_ENGINE_HPP
#define HYPER_VSA_ENGINE_HPP

#include <immintrin.h>
#include <cstdint>
#include <cstddef>
#include <cmath>

#define VSA_DIMENSION_BITS 8192
#define VSA_VEC256_COUNT   (VSA_DIMENSION_BITS / 256) // 32 AVX2 registers
#define VSA_ALIGNMENT      32

#if defined(_MSC_VER)
    #define HYPER_RESTRICT __restrict
    #define HYPER_INLINE __forceinline
    #define HYPER_EXPORT __declspec(dllexport)
#else
    #define HYPER_RESTRICT __restrict__
    #define HYPER_INLINE inline __attribute__((always_inline))
    #define HYPER_EXPORT __attribute__((visibility("default")))
#endif

namespace hyper::vsa {

/**
 * 8192-bit Hypervector aligned to 32-byte cache line boundaries.
 * Fits within the 32KB L1 Data Cache of an Intel Golden Cove P-core.
 */
struct alignas(VSA_ALIGNMENT) BinaryHypervector {
    __m256i words[VSA_VEC256_COUNT];

    HYPER_INLINE void clear() {
        __m256i zero = _mm256_setzero_si256();
        for (size_t i = 0; i < VSA_VEC256_COUNT; ++i) {
            words[i] = zero;
        }
    }
};

/**
 * Projection Basis Matrix: Continuous R^d -> Binary {0, 1}^D
 */
struct alignas(VSA_ALIGNMENT) ProjectionBasis {
    size_t in_dim;             // Continuous dimension d (e.g. 128)
    size_t out_bits;           // Hyperdimensional dimension D (e.g. 8192)
    const float* weights;      // Flattened [out_bits * in_dim] FP32 weights
};

/**
 * Fast AVX2 Vectorized 4-bit Parallel Popcount (Muła's Algorithm via PSHUFB)
 * Bypasses missing AVX2 SIMD popcount by evaluating 32 bytes simultaneously 
 * using an in-register nibble lookup table. Zero RAM traffic.
 */
HYPER_INLINE uint32_t avx2_popcount256(__m256i v) {
    const __m256i lookup = _mm256_setr_epi8(
        0, 1, 1, 2, 1, 2, 2, 3, 1, 2, 2, 3, 2, 3, 3, 4,
        0, 1, 1, 2, 1, 2, 2, 3, 1, 2, 2, 3, 2, 3, 3, 4
    );
    const __m256i low_mask = _mm256_set1_epi8(0x0F);

    __m256i lo = _mm256_and_si256(v, low_mask);
    __m256i hi = _mm256_and_si256(_mm256_srli_epi16(v, 4), low_mask);

    __m256i cnt1 = _mm256_shuffle_epi8(lookup, lo);
    __m256i cnt2 = _mm256_shuffle_epi8(lookup, hi);

    __m256i sum = _mm256_add_epi8(cnt1, cnt2);
    __m256i sad = _mm256_sad_epu8(sum, _mm256_setzero_si256());

    uint64_t w0 = _mm256_extract_epi64(sad, 0);
    uint64_t w1 = _mm256_extract_epi64(sad, 1);
    uint64_t w2 = _mm256_extract_epi64(sad, 2);
    uint64_t w3 = _mm256_extract_epi64(sad, 3);

    return static_cast<uint32_t>(w0 + w1 + w2 + w3);
}

/**
 * Unrolled AVX2 Popcount across full 8192-bit hypervector.
 */
HYPER_INLINE uint32_t avx2_popcount_hypervector(const BinaryHypervector& hv) {
    uint32_t total = 0;
    for (size_t i = 0; i < VSA_VEC256_COUNT; i += 4) {
        total += avx2_popcount256(hv.words[i]);
        total += avx2_popcount256(hv.words[i + 1]);
        total += avx2_popcount256(hv.words[i + 2]);
        total += avx2_popcount256(hv.words[i + 3]);
    }
    return total;
}

extern "C" {

HYPER_EXPORT void vsa_pin_to_pcores();

HYPER_EXPORT void vsa_project_fp32_to_binary(
    const float* HYPER_RESTRICT input,
    const float* HYPER_RESTRICT basis_weights,
    size_t in_dim,
    size_t out_bits,
    uint32_t* HYPER_RESTRICT output_bits
);

HYPER_EXPORT void vsa_bind_avx2(
    const uint32_t* HYPER_RESTRICT a,
    const uint32_t* HYPER_RESTRICT b,
    uint32_t* HYPER_RESTRICT out,
    size_t num_words256
);

HYPER_EXPORT uint32_t vsa_hamming_distance_avx2(
    const uint32_t* HYPER_RESTRICT a,
    const uint32_t* HYPER_RESTRICT b,
    size_t num_words256
);

HYPER_EXPORT void vsa_gemm_surrogate_avx2(
    const uint32_t* HYPER_RESTRICT projected_input,
    const uint32_t* HYPER_RESTRICT binary_codebook,
    size_t num_outputs,
    size_t num_words256,
    float* HYPER_RESTRICT output_similarities
);

HYPER_EXPORT void vsa_bundle_majority_avx2(
    const uint32_t* const* HYPER_RESTRICT vectors,
    size_t k,
    size_t num_words256,
    uint32_t* HYPER_RESTRICT consensus_out
);

} // extern "C"

} // namespace hyper::vsa

#endif // HYPER_VSA_ENGINE_HPP
