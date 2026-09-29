/**
 * PROJECT LEO (HYPER) - MASTER BYPASS ARCHITECTURE
 * FILE: kernels/vsa/hyper_vsa_10k_engine.cpp
 * 
 * Implementation of Pillar 1: Vector Symbolic Architecture 10,000-Bit Surrogate Engine.
 * Tailored for Intel Core i5-12450H Golden Cove P-Cores with AVX2.
 */

#include "hyper_vsa_10k_engine.hpp"
#include <cstring>
#include <cmath>

#ifdef _WIN32
#ifndef WIN32_LEAN_AND_MEAN
#define WIN32_LEAN_AND_MEAN
#endif
#include <windows.h>
#endif

namespace hyper::vsa {

extern "C" {

HYPER_EXPORT int vsa_10k_pin_pcores() {
#ifdef _WIN32
    HANDLE hThread = GetCurrentThread();
    // 0x0F pins to logical cores 0, 1, 2, 3 (The 4 Golden Cove P-Cores of the i5-12450H)
    DWORD_PTR mask = 0x0F;
    if (SetThreadAffinityMask(hThread, mask) == 0) {
        return -1;
    }
    return 0;
#else
    return 0;
#endif
}

HYPER_EXPORT void vsa_10k_project_fp32(
    const float* HYPER_RESTRICT input,
    const float* HYPER_RESTRICT basis_matrix,
    size_t in_dim,
    uint32_t* HYPER_RESTRICT out_bits
) {
    if (!input || !basis_matrix || !out_bits || in_dim == 0) return;

    // Zero the entire 10,240-bit buffer (320 uint32_t words)
    std::memset(out_bits, 0, VSA_10K_U32_WORDS * sizeof(uint32_t));

    // Project each bit b in [0, 10000) via sign(dot(basis[b], input))
    for (size_t b = 0; b < VSA_10K_TARGET_BITS; ++b) {
        const float* row = basis_matrix + (b * in_dim);
        __m256 acc = _mm256_setzero_ps();
        size_t d = 0;

        for (; d + 8 <= in_dim; d += 8) {
            __m256 x = _mm256_loadu_ps(input + d);
            __m256 w = _mm256_loadu_ps(row + d);
            acc = _mm256_fmadd_ps(x, w, acc);
        }

        // Horizontal sum of acc
        __m128 lo = _mm256_castps256_ps128(acc);
        __m128 hi = _mm256_extractf128_ps(acc, 1);
        __m128 sum4 = _mm_add_ps(lo, hi);
        sum4 = _mm_hadd_ps(sum4, sum4);
        sum4 = _mm_hadd_ps(sum4, sum4);
        float dot_val = _mm_cvtss_f32(sum4);

        // Add tail elements
        for (; d < in_dim; ++d) {
            dot_val += input[d] * row[d];
        }

        if (dot_val > 0.0f) {
            out_bits[b >> 5] |= (1u << (b & 31));
        }
    }
}

HYPER_EXPORT void vsa_10k_bind_xor(
    const uint32_t* HYPER_RESTRICT a,
    const uint32_t* HYPER_RESTRICT b,
    uint32_t* HYPER_RESTRICT out
) {
    const __m256i* va = reinterpret_cast<const __m256i*>(a);
    const __m256i* vb = reinterpret_cast<const __m256i*>(b);
    __m256i* vout = reinterpret_cast<__m256i*>(out);

    // Exactly 40 AVX2 registers for 10,240 bits
    #pragma loop(no_vector)
    for (size_t i = 0; i < VSA_10K_AVX2_WORDS; i += 4) {
        vout[i]     = _mm256_xor_si256(va[i],     vb[i]);
        vout[i + 1] = _mm256_xor_si256(va[i + 1], vb[i + 1]);
        vout[i + 2] = _mm256_xor_si256(va[i + 2], vb[i + 2]);
        vout[i + 3] = _mm256_xor_si256(va[i + 3], vb[i + 3]);
    }
}

HYPER_EXPORT uint32_t vsa_10k_hamming_distance(
    const uint32_t* HYPER_RESTRICT a,
    const uint32_t* HYPER_RESTRICT b
) {
    const uint64_t* ua = reinterpret_cast<const uint64_t*>(a);
    const uint64_t* ub = reinterpret_cast<const uint64_t*>(b);
    uint64_t total_diff = 0;

    // 160 uint64_t words
    for (size_t i = 0; i < VSA_10K_U64_WORDS; i += 4) {
        total_diff += _mm_popcnt_u64(ua[i]     ^ ub[i]);
        total_diff += _mm_popcnt_u64(ua[i + 1] ^ ub[i + 1]);
        total_diff += _mm_popcnt_u64(ua[i + 2] ^ ub[i + 2]);
        total_diff += _mm_popcnt_u64(ua[i + 3] ^ ub[i + 3]);
    }

    return static_cast<uint32_t>(total_diff);
}

HYPER_EXPORT void vsa_10k_gemm_surrogate(
    const uint32_t* HYPER_RESTRICT projected_input,
    const uint32_t* HYPER_RESTRICT codebook_hypervectors,
    size_t num_outputs,
    float* HYPER_RESTRICT output_similarities
) {
    if (!projected_input || !codebook_hypervectors || !output_similarities) return;

    constexpr float D = static_cast<float>(VSA_10K_TARGET_BITS);
    constexpr float PI = 3.14159265358979323846f;

    for (size_t k = 0; k < num_outputs; ++k) {
        const uint32_t* cb_vec = codebook_hypervectors + (k * VSA_10K_U32_WORDS);
        uint32_t d_H = vsa_10k_hamming_distance(projected_input, cb_vec);
        
        // Cap to valid bit range
        if (d_H > VSA_10K_TARGET_BITS) d_H = VSA_10K_TARGET_BITS;

        // Charikar's exact cosine isomorphism: cos(pi * d_H / D)
        output_similarities[k] = std::cos(PI * (static_cast<float>(d_H) / D));
    }
}

HYPER_EXPORT void vsa_10k_bundle_majority(
    const uint32_t* const* HYPER_RESTRICT vectors,
    size_t k,
    uint32_t* HYPER_RESTRICT consensus_out
) {
    if (!vectors || k == 0 || !consensus_out) return;

    std::memset(consensus_out, 0, VSA_10K_U32_WORDS * sizeof(uint32_t));
    const size_t threshold = k / 2;

    for (size_t b = 0; b < VSA_10K_TARGET_BITS; ++b) {
        const size_t word_idx = b >> 5;
        const uint32_t bit_mask = (1u << (b & 31));
        size_t votes = 0;

        for (size_t i = 0; i < k; ++i) {
            if (vectors[i][word_idx] & bit_mask) {
                votes++;
            }
        }

        if (votes > threshold) {
            consensus_out[word_idx] |= bit_mask;
        }
    }
}

} // extern "C"

} // namespace hyper::vsa
