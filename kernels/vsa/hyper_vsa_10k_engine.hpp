/**
 * PROJECT LEO (HYPER) - MASTER BYPASS ARCHITECTURE
 * FILE: kernels/vsa/hyper_vsa_10k_engine.hpp
 * 
 * PILLAR 1: Vector Symbolic Architecture (VSA) 10,000-Bit Surrogate Engine
 * Hardware Target: Intel Core i5-12450H (4 Golden Cove P-Cores, AVX2, Windows 11).
 * 
 * Objective: Replace dense FP32/FP16 matrix multiplications (W * X + B) with
 * 10,000-bit hypervector XOR binding and vectorized population count bundling.
 */

#pragma once

#ifndef HYPER_VSA_10K_ENGINE_HPP
#define HYPER_VSA_10K_ENGINE_HPP

#include <immintrin.h>
#include <cstdint>
#include <cstddef>
#include <cmath>

// 10,000 bits rounded up to next 256-bit AVX2 boundary = 10,240 bits (40 * 256-bit registers = 1,280 bytes)
#define VSA_10K_TARGET_BITS     10000
#define VSA_10K_PADDED_BITS     10240
#define VSA_10K_AVX2_WORDS      (VSA_10K_PADDED_BITS / 256) // Exactly 40 registers
#define VSA_10K_U64_WORDS       (VSA_10K_PADDED_BITS / 64)  // Exactly 160 uint64_t words
#define VSA_10K_U32_WORDS       (VSA_10K_PADDED_BITS / 32)  // Exactly 320 uint32_t words
#define VSA_10K_ALIGNMENT       64                          // Cacheline aligned (64 bytes)

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
 * 10,240-bit Hypervector aligned to 64-byte cacheline boundaries.
 * 1,280 bytes fits cleanly within the 48KB L1 Data Cache of an Intel Golden Cove P-core.
 */
struct alignas(VSA_10K_ALIGNMENT) Hypervector10K {
    union {
        __m256i  v256[VSA_10K_AVX2_WORDS];
        uint64_t u64[VSA_10K_U64_WORDS];
        uint32_t u32[VSA_10K_U32_WORDS];
        uint8_t  u8[1280];
    };

    HYPER_INLINE void zero() {
        __m256i z = _mm256_setzero_si256();
        for (size_t i = 0; i < VSA_10K_AVX2_WORDS; ++i) {
            v256[i] = z;
        }
    }
};

/**
 * Continuous to Hypervector Projection Basis (R^d -> {0, 1}^10000).
 */
struct alignas(VSA_10K_ALIGNMENT) ProjectionBasis10K {
    size_t in_dim;               // Input continuous dimension d
    size_t out_bits;             // 10,000 bits
    const float* basis_matrix;   // [out_bits * in_dim] row-major FP32 weights
};

/**
 * AVX2 Hardware-Accelerated 64-bit Popcount Accumulator.
 * Unrolls across 4 uint64_t lanes per 256-bit register using hardware _mm_popcnt_u64.
 */
HYPER_INLINE uint32_t avx2_popcount_10k(const Hypervector10K& hv) {
    uint64_t total = 0;
    const uint64_t* ptr = hv.u64;

    #pragma loop(no_vector)
    for (size_t i = 0; i < VSA_10K_U64_WORDS; i += 8) {
        total += _mm_popcnt_u64(ptr[i]);
        total += _mm_popcnt_u64(ptr[i + 1]);
        total += _mm_popcnt_u64(ptr[i + 2]);
        total += _mm_popcnt_u64(ptr[i + 3]);
        total += _mm_popcnt_u64(ptr[i + 4]);
        total += _mm_popcnt_u64(ptr[i + 5]);
        total += _mm_popcnt_u64(ptr[i + 6]);
        total += _mm_popcnt_u64(ptr[i + 7]);
    }
    return static_cast<uint32_t>(total);
}

/**
 * In-register AVX2 256-bit SIMD Popcount via PSHUFB nibble lookup.
 * Eliminates integer register roundtrips when evaluating intermediate bindings.
 */
HYPER_INLINE __m256i avx2_pshufb_popcount256(__m256i v) {
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
    return _mm256_sad_epu8(sum, _mm256_setzero_si256());
}

extern "C" {

/**
 * Pins calling thread strictly to Intel Core i5-12450H Golden Cove P-Cores (Logical Processors 0..3).
 */
HYPER_EXPORT int vsa_10k_pin_pcores();

/**
 * Projects continuous input tensor x in R^d into 10,000-bit pseudo-orthogonal hypervector.
 */
HYPER_EXPORT void vsa_10k_project_fp32(
    const float* HYPER_RESTRICT input,
    const float* HYPER_RESTRICT basis_matrix,
    size_t in_dim,
    uint32_t* HYPER_RESTRICT out_bits
);

/**
 * Hypervector Bitwise Binding: C = A XOR B.
 * Replaces dense FMA (Fused Multiply-Add) via _mm256_xor_si256.
 */
HYPER_EXPORT void vsa_10k_bind_xor(
    const uint32_t* HYPER_RESTRICT a,
    const uint32_t* HYPER_RESTRICT b,
    uint32_t* HYPER_RESTRICT out
);

/**
 * Computes Hamming Distance between two 10,000-bit hypervectors via AVX2 XOR + _mm_popcnt_u64.
 */
HYPER_EXPORT uint32_t vsa_10k_hamming_distance(
    const uint32_t* HYPER_RESTRICT a,
    const uint32_t* HYPER_RESTRICT b
);

/**
 * Evaluates VSA GEMM Surrogate:
 * Computes cosine similarity to a codebook of N candidate outputs using Charikar's formula:
 * cos(pi * d_H / 10000).
 */
HYPER_EXPORT void vsa_10k_gemm_surrogate(
    const uint32_t* HYPER_RESTRICT projected_input,
    const uint32_t* HYPER_RESTRICT codebook_hypervectors,
    size_t num_outputs,
    float* HYPER_RESTRICT output_similarities
);

/**
 * Majority Bundling: Bundles K hypervectors via majority voting into a single consensus vector.
 */
HYPER_EXPORT void vsa_10k_bundle_majority(
    const uint32_t* const* HYPER_RESTRICT vectors,
    size_t k,
    uint32_t* HYPER_RESTRICT consensus_out
);

} // extern "C"

} // namespace hyper::vsa

#endif // HYPER_VSA_10K_ENGINE_HPP
