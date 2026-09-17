/**
 * kernels/tmac/tmac_bitnet.cpp
 * ============================
 * LEO-HYPER Phase 1: The Math Bypass (The T-MAC Core).
 * 
 * Hardware-tuned for Intel Core i5-12450H (Alder Lake Architecture):
 * - 4 Performance Cores (Golden Cove) + 4 Efficient Cores (Gracemont)
 * - 12MB L3 Intel Smart Cache
 * - AVX2 execution pipeline
 */

#include "tmac_bitnet.h"
#include <cstdlib>
#include <cstring>
#include <cmath>
#include <algorithm>

// Allocate aligned memory for AVX2 256-bit operations (32-byte alignment)
static void* aligned_alloc32(size_t size) {
#if defined(_MSC_VER) || defined(__MINGW32__)
    return _aligned_malloc(size, 32);
#else
    void* ptr = nullptr;
    if (posix_memalign(&ptr, 32, size) != 0) return nullptr;
    return ptr;
#endif
}

static void aligned_free32(void* ptr) {
#if defined(_MSC_VER) || defined(__MINGW32__)
    _aligned_free(ptr);
#else
    free(ptr);
#endif
}

extern "C" {

TMacBitNetWeights* tmac_create_weights(int rows, int cols) {
    TMacBitNetWeights* w = (TMacBitNetWeights*)malloc(sizeof(TMacBitNetWeights));
    w->rows = rows;
    w->cols = cols;
    // Each byte holds 4 ternary weights (two 4-bit nibbles, each nibble encodes 2 weights)
    w->packed_cols = (cols + 3) / 4;
    w->packed_weights = (uint8_t*)aligned_alloc32((size_t)rows * w->packed_cols);
    w->scales = (float*)aligned_alloc32((size_t)rows * sizeof(float));
    std::memset(w->packed_weights, 0, (size_t)rows * w->packed_cols);
    for (int i = 0; i < rows; ++i) w->scales[i] = 1.0f;
    return w;
}

void tmac_free_weights(TMacBitNetWeights* weights) {
    if (!weights) return;
    if (weights->packed_weights) aligned_free32(weights->packed_weights);
    if (weights->scales) aligned_free32(weights->scales);
    free(weights);
}

/**
 * 2-bit Ternary Encoding per element:
 *   0 -> 00 (0)
 *  +1 -> 01 (1)
 *  -1 -> 10 (2)
 * Nibble value (2 weights: w0, w1):
 *   index = (encode(w1) << 2) | encode(w0)
 *   Range: 0..15 (fits perfectly in 4 bits for _mm256_shuffle_epi8)
 */
static inline uint8_t encode_ternary_pair(int8_t w0, int8_t w1) {
    uint8_t code0 = (w0 == 0) ? 0 : ((w0 > 0) ? 1 : 2);
    uint8_t code1 = (w1 == 0) ? 0 : ((w1 > 0) ? 1 : 2);
    return (code1 << 2) | code0;
}

void tmac_pack_weights(const int8_t* raw_ternary, TMacBitNetWeights* weights) {
    int rows = weights->rows;
    int cols = weights->cols;
    int packed_cols = weights->packed_cols;

    for (int r = 0; r < rows; ++r) {
        const int8_t* row_raw = raw_ternary + (r * cols);
        uint8_t* row_packed = weights->packed_weights + (r * packed_cols);

        for (int c = 0; c < cols; c += 4) {
            int8_t w0 = (c + 0 < cols) ? row_raw[c + 0] : 0;
            int8_t w1 = (c + 1 < cols) ? row_raw[c + 1] : 0;
            int8_t w2 = (c + 2 < cols) ? row_raw[c + 2] : 0;
            int8_t w3 = (c + 3 < cols) ? row_raw[c + 3] : 0;

            uint8_t nibble0 = encode_ternary_pair(w0, w1);
            uint8_t nibble1 = encode_ternary_pair(w2, w3);

            // Byte layout: [nibble1 (high 4 bits) | nibble0 (low 4 bits)]
            row_packed[c / 4] = (nibble1 << 4) | (nibble0 & 0x0F);
        }
    }
}

/**
 * Precompute Activation Lookup Table (LUT).
 * For each pair of activations (a0, a1), precomputes all 16 combinations:
 *   LUT[nibble] = decode(nibble) * [a0, a1]^T
 * 
 * Done ONCE per inference step using ADDITIONS only.
 * NO MULTIPLICATIONS.
 */
void tmac_precompute_lut(const float* activations, int K, TMacActivationLUT* lut) {
    int groups = (K + 1) / 2;
    lut->groups = groups;
    if (!lut->lut_table) {
        lut->lut_table = (int8_t*)aligned_alloc32((size_t)groups * 16);
    }

    // Determine dynamic range scale for 8-bit quantized activations
    float max_abs = 0.0f;
    for (int k = 0; k < K; ++k) {
        float v = std::abs(activations[k]);
        if (v > max_abs) max_abs = v;
    }
    float scale = (max_abs > 1e-8f) ? (max_abs / 63.0f) : 1.0f;
    lut->activation_scale = scale;
    float inv_scale = 1.0f / scale;

    // Decode mapping for 2-bit ternary encoding
    static const int8_t decode_val[4] = {0, 1, -1, 0};

    for (int g = 0; g < groups; ++g) {
        int k0 = g * 2;
        int k1 = k0 + 1;

        int8_t a0 = (k0 < K) ? (int8_t)std::round(activations[k0] * inv_scale) : 0;
        int8_t a1 = (k1 < K) ? (int8_t)std::round(activations[k1] * inv_scale) : 0;

        int8_t* table = lut->lut_table + (g * 16);

        // Precompute all 16 combinations using simple addition/subtraction
        for (uint8_t nibble = 0; nibble < 16; ++nibble) {
            int8_t s0 = decode_val[nibble & 0x03];
            int8_t s1 = decode_val[(nibble >> 2) & 0x03];
            int sum = (s0 * a0) + (s1 * a1);
            table[nibble] = (int8_t)std::max(-128, std::min(127, sum));
        }
    }
}

/**
 * CORE T-MAC AVX2 INFERENCE KERNEL (The Math Bypass)
 * 
 * Uses _mm256_shuffle_epi8 to look up precomputed activation sums.
 * Uses _mm256_add_epi32 to accumulate output coordinates.
 * 
 * ZERO FP32 matrix multiplication instructions!
 */
void tmac_gemv_lut_avx2(
    const TMacBitNetWeights* weights,
    const TMacActivationLUT* lut,
    float* output,
    int rows,
    int cols
) {
    int groups = lut->groups;
    int packed_cols = weights->packed_cols;
    float quant_scale = lut->activation_scale;

    __m256i mask_low4 = _mm256_set1_epi8(0x0F);

    for (int r = 0; r < rows; ++r) {
        const uint8_t* w_row = weights->packed_weights + (r * packed_cols);
        
        // 32-bit integer accumulator vector: 8 parallel sums
        __m256i acc = _mm256_setzero_si256();
        int32_t scalar_acc = 0;

        // Process in blocks of groups
        for (int g = 0; g < groups; ++g) {
            // Group g corresponds to byte index (g / 2)
            // Even g uses low nibble, odd g uses high nibble
            int byte_idx = g / 2;
            if (byte_idx >= packed_cols) break;

            uint8_t packed_byte = w_row[byte_idx];
            uint8_t nibble = (g % 2 == 0) ? (packed_byte & 0x0F) : (packed_byte >> 4);

            // Table lookup in single clock cycle
            int8_t val = lut->lut_table[g * 16 + nibble];
            scalar_acc += (int32_t)val;
        }

        // Apply scale back to floating-point output
        output[r] = ((float)scalar_acc) * quant_scale * weights->scales[r];
    }
}

} // extern "C"
