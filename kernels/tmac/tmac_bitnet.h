/**
 * kernels/tmac/tmac_bitnet.h
 * ==========================
 * LEO-HYPER Phase 1: The Math Bypass (The T-MAC Core).
 * 
 * Objective: Eliminate matrix multiplication (MAC) from the inference loop.
 * Architecture: Intel Core i5-12450H (AVX2, 12MB L3 Cache, Shared RAM).
 * Target Model: BitNet b1.58 (Ternary weights {-1, 0, +1}).
 * 
 * Mechanism:
 * - 2-bit packed ternary weights: 4 weights per byte (two 4-bit nibbles).
 * - Precomputed Activation Lookup Tables (LUT) per group.
 * - Hardware SIMD table lookup using _mm256_shuffle_epi8 (pshufb).
 * - Integer vector accumulation using _mm256_add_epi32.
 * - ZERO FP32 / FP16 multiplication in the inner token generation loop.
 */

#ifndef TMAC_BITNET_H
#define TMAC_BITNET_H

#include <immintrin.h>
#include <cstdint>
#include <cstddef>

#ifdef __cplusplus
extern "C" {
#endif

// Weight packing configuration:
// 2 weights per 4-bit nibble (values 0..15).
// Encoding: 00 = 0, 01 = +1, 10 = -1, 11 = 0
#define TMAC_GROUP_SIZE 2
#define TMAC_LUT_ENTRIES 16

typedef struct {
    int rows;              // Output features (N)
    int cols;              // Input features (K)
    int packed_cols;       // K / 4 bytes
    uint8_t* packed_weights; // 2-bit packed ternary weights
    float* scales;         // Per-channel output scales
} TMacBitNetWeights;

typedef struct {
    int groups;            // K / 2 groups
    int8_t* lut_table;     // Pre-computed lookup tables (groups * 16 bytes)
    float activation_scale;// Dynamic quant scale for activations
} TMacActivationLUT;

/**
 * Initialize packed ternary weights for BitNet b1.58.
 */
TMacBitNetWeights* tmac_create_weights(int rows, int cols);
void tmac_free_weights(TMacBitNetWeights* weights);

/**
 * Pack ternary weights {-1, 0, +1} into 2-bit nibbles.
 */
void tmac_pack_weights(
    const int8_t* raw_ternary, 
    TMacBitNetWeights* weights
);

/**
 * Precompute Activation Lookup Table (LUT).
 * Calculates all linear combinations of 2 activations using additions only.
 * NO floating-point matrix multiplication.
 */
void tmac_precompute_lut(
    const float* activations, 
    int K, 
    TMacActivationLUT* lut
);

/**
 * Core T-MAC AVX2 Inference Kernel (The Math Bypass).
 * Evaluates Y = W * X using ONLY _mm256_shuffle_epi8 and _mm256_add_epi32.
 * Floating-point multiplier ports remain 100% idle.
 */
void tmac_gemv_lut_avx2(
    const TMacBitNetWeights* weights,
    const TMacActivationLUT* lut,
    float* output,
    int rows,
    int cols
);

#ifdef __cplusplus
}
#endif

#endif // TMAC_BITNET_H
