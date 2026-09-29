/**
 * PROJECT LEO / HYPER: C++ NATIVE ACCELERATION BACKEND
 * FILE: kernels/vsa/hyper_vsa_engine.cpp
 * 
 * Vector Symbolic Architecture (VSA) Native AVX2 Implementation
 * Optimized for Intel Core i5-12450H Golden Cove P-Cores.
 */

#include "hyper_vsa_engine.hpp"

#ifdef _WIN32
#ifndef WIN32_LEAN_AND_MEAN
#define WIN32_LEAN_AND_MEAN
#endif
#include <windows.h>
#endif

namespace hyper::vsa {

extern "C" {

/**
 * Pins the calling thread strictly to the 4 Golden Cove P-Cores (Cores 0-3).
 * Prevents OS thread migration to Gracemont E-Cores during heavy SIMD loops.
 */
HYPER_EXPORT void vsa_pin_to_pcores() {
#ifdef _WIN32
    HANDLE hThread = GetCurrentThread();
    // Bitmask 0x0F pins to logical processors 0, 1, 2, 3
    DWORD_PTR affinityMask = 0x0F;
    SetThreadAffinityMask(hThread, affinityMask);
#endif
}

/**
 * Projects a continuous FP32 activation vector to an unrolled binary hypervector.
 * For each output bit i, computes dot(input, basis_weights[i]) and sets bit if < 0.
 */
HYPER_EXPORT void vsa_project_fp32_to_binary(
    const float* HYPER_RESTRICT input,
    const float* HYPER_RESTRICT basis_weights,
    size_t in_dim,
    size_t out_bits,
    uint32_t* HYPER_RESTRICT output_bits
) {
    size_t num_u32 = (out_bits + 31) / 32;
    for (size_t b = 0; b < num_u32; ++b) {
        output_bits[b] = 0;
    }

    for (size_t bit = 0; bit < out_bits; ++bit) {
        const float* row = basis_weights + bit * in_dim;
        __m256 sum256 = _mm256_setzero_ps();

        size_t d = 0;
        for (; d + 8 <= in_dim; d += 8) {
            __m256 in_vec = _mm256_loadu_ps(input + d);
            __m256 w_vec  = _mm256_loadu_ps(row + d);
            sum256 = _mm256_fmadd_ps(in_vec, w_vec, sum256);
        }

        // Horizontal reduction of sum256
        __m128 lo = _mm256_castps256_ps128(sum256);
        __m128 hi = _mm256_extractf128_ps(sum256, 1);
        __m128 sum128 = _mm_add_ps(lo, hi);
        sum128 = _mm_hadd_ps(sum128, sum128);
        sum128 = _mm_hadd_ps(sum128, sum128);
        float total = _mm_cvtss_f32(sum128);

        // Scalar tail
        for (; d < in_dim; ++d) {
            total += input[d] * row[d];
        }

        // Quantization: If total < 0, set bit to 1; else 0
        if (total < 0.0f) {
            output_bits[bit / 32] |= (1u << (bit % 32));
        }
    }
}

/**
 * 256-bit SIMD Hypervector Binding (XOR)
 */
HYPER_EXPORT void vsa_bind_avx2(
    const uint32_t* HYPER_RESTRICT a,
    const uint32_t* HYPER_RESTRICT b,
    uint32_t* HYPER_RESTRICT out,
    size_t num_words256
) {
    const __m256i* va = reinterpret_cast<const __m256i*>(a);
    const __m256i* vb = reinterpret_cast<const __m256i*>(b);
    __m256i* vout = reinterpret_cast<__m256i*>(out);

    for (size_t i = 0; i < num_words256; ++i) {
        __m256i x = _mm256_loadu_si256(va + i);
        __m256i y = _mm256_loadu_si256(vb + i);
        _mm256_storeu_si256(vout + i, _mm256_xor_si256(x, y));
    }
}

/**
 * High-Throughput In-Register Hamming Distance via Parallel AVX2 Popcount
 */
HYPER_EXPORT uint32_t vsa_hamming_distance_avx2(
    const uint32_t* HYPER_RESTRICT a,
    const uint32_t* HYPER_RESTRICT b,
    size_t num_words256
) {
    const __m256i* va = reinterpret_cast<const __m256i*>(a);
    const __m256i* vb = reinterpret_cast<const __m256i*>(b);

    uint32_t total_dist = 0;
    for (size_t i = 0; i < num_words256; ++i) {
        __m256i diff = _mm256_xor_si256(_mm256_loadu_si256(va + i), _mm256_loadu_si256(vb + i));
        total_dist += avx2_popcount256(diff);
    }
    return total_dist;
}

/**
 * Dense GEMM Surrogate Kernel: Computes output activations directly from
 * pairwise Hamming distances against binary codebook centroids.
 */
HYPER_EXPORT void vsa_gemm_surrogate_avx2(
    const uint32_t* HYPER_RESTRICT projected_input,
    const uint32_t* HYPER_RESTRICT binary_codebook,
    size_t num_outputs,
    size_t num_words256,
    float* HYPER_RESTRICT output_similarities
) {
    const float total_bits = static_cast<float>(num_words256 * 256);
    const float inv_bits = 1.0f / total_bits;

    for (size_t k = 0; k < num_outputs; ++k) {
        const uint32_t* codebook_row = binary_codebook + k * (num_words256 * 8);
        uint32_t d_h = vsa_hamming_distance_avx2(projected_input, codebook_row, num_words256);
        
        // Charikar's Theorem: cos(theta) = cos(pi * d_H / D)
        float normalized_dist = static_cast<float>(d_h) * inv_bits;
        output_similarities[k] = std::cos(3.14159265358979323846f * normalized_dist);
    }
}

/**
 * Hyperdimensional Majority Rule Bundling
 */
HYPER_EXPORT void vsa_bundle_majority_avx2(
    const uint32_t* const* HYPER_RESTRICT vectors,
    size_t k,
    size_t num_words256,
    uint32_t* HYPER_RESTRICT consensus_out
) {
    size_t total_u32 = num_words256 * 8;
    const uint32_t threshold = static_cast<uint32_t>(k / 2);

    for (size_t w = 0; w < total_u32; ++w) {
        uint32_t word_accum = 0;
        for (int bit = 0; bit < 32; ++bit) {
            uint32_t count = 0;
            uint32_t bitmask = (1u << bit);
            for (size_t vi = 0; vi < k; ++vi) {
                if (vectors[vi][w] & bitmask) {
                    count++;
                }
            }
            if (count > threshold) {
                word_accum |= bitmask;
            }
        }
        consensus_out[w] = word_accum;
    }
}

} // extern "C"

} // namespace hyper::vsa
