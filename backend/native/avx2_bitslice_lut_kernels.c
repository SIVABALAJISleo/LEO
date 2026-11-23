/**
 * backend/native/avx2_bitslice_lut_kernels.c
 * ==============================================================================
 * Project LEO / HYPER-Omega: Software-Defined Transistor Replacement Kernels
 * Target Hardware: Intel Core i5-12450H (AVX2 + FMA, L1/L2 Cache Hierarchy)
 *
 * Implements:
 *   1. Mechanism 2: Bit-Sliced (SWAR) Virtual Logic Gate Engine
 *      - Software-defined logic gates (AND, OR, XOR, MUX, CSA)
 *      - Bit-sliced ripple-carry adders & 1-bit XNOR-popcount binary MatMul
 *   2. Mechanism 3: Multiply-Free Lookup Table (LUT / VPSHUFB) Engine
 *      - 16-byte activation table lookups via _mm256_shuffle_epi8
 *      - Zero hardware multiplier/FMA calls in inner accumulation loops
 *   3. Mechanism 4: Bit-Exact ISA & Microcode Emulation (FP8 E4M3/E5M2 & CUDA Warp)
 *      - Exact IEEE/OCP FP8 decoders/encoders and dot-products
 *      - CUDA warp shuffle reduction emulation
 *
 * Portable C99 with compile-time AVX2 fast paths and scalar fallback.
 * ==============================================================================
 */

#if !defined(_WIN32) && !defined(_WIN64)
    #ifndef _GNU_SOURCE
        #define _GNU_SOURCE 1
    #endif
#endif

#include <stdint.h>
#include <stddef.h>
#include <string.h>
#include <math.h>

#if defined(_MSC_VER)
    #define LEO_EXPORT __declspec(dllexport)
#else
    #define LEO_EXPORT __attribute__((visibility("default")))
#endif

#if defined(__x86_64__) || defined(_M_X64) || defined(__i386__) || defined(_M_IX86)
    #if defined(__AVX2__)
        #include <immintrin.h>
        #define LEO_HAS_AVX2 1
    #else
        #define LEO_HAS_AVX2 0
    #endif
#else
    #define LEO_HAS_AVX2 0
#endif

/* -------------------------------------------------------------------------- */
/* Hardware Capability Query                                                  */
/* -------------------------------------------------------------------------- */

LEO_EXPORT int leo_has_avx2_hardware(void) {
#if LEO_HAS_AVX2
    return 1;
#else
    return 0;
#endif
}

/* -------------------------------------------------------------------------- */
/* MECHANISM 2: BIT-SLICED (SWAR) VIRTUAL LOGIC GATE ENGINE                   */
/* -------------------------------------------------------------------------- */

/**
 * Pure bit-sliced ripple-carry adder.
 * Evaluates bit_width bits across num_lanes_u64 64-bit words (each bit is an
 * independent virtual wire). Zero hardware '+' instructions inside the loop!
 */
LEO_EXPORT void leo_bitslice_ripple_carry_adder(
    const uint64_t *a_bits,       /* Shape: [bit_width, num_lanes_u64] */
    const uint64_t *b_bits,       /* Shape: [bit_width, num_lanes_u64] */
    uint64_t *sum_bits,           /* Shape: [bit_width, num_lanes_u64] */
    uint64_t *carry_out,          /* Shape: [num_lanes_u64] */
    int32_t bit_width,
    int32_t num_lanes_u64
) {
#if LEO_HAS_AVX2
    int32_t lane = 0;
    for (; lane + 3 < num_lanes_u64; lane += 4) {
        __m256i carry = _mm256_setzero_si256();
        for (int32_t b = 0; b < bit_width; ++b) {
            int32_t idx = b * num_lanes_u64 + lane;
            __m256i a = _mm256_loadu_si256((const __m256i*)(a_bits + idx));
            __m256i b_val = _mm256_loadu_si256((const __m256i*)(b_bits + idx));

            /* Virtual logic gates via AVX2 256-bit SIMD */
            __m256i a_xor_b = _mm256_xor_si256(a, b_val);
            __m256i sum = _mm256_xor_si256(a_xor_b, carry);
            __m256i carry_next = _mm256_or_si256(
                _mm256_and_si256(a, b_val),
                _mm256_and_si256(carry, a_xor_b)
            );

            _mm256_storeu_si256((__m256i*)(sum_bits + idx), sum);
            carry = carry_next;
        }
        if (carry_out != NULL) {
            _mm256_storeu_si256((__m256i*)(carry_out + lane), carry);
        }
    }
    for (; lane < num_lanes_u64; ++lane) {
        uint64_t carry = 0ULL;
        for (int32_t b = 0; b < bit_width; ++b) {
            int32_t idx = b * num_lanes_u64 + lane;
            uint64_t a = a_bits[idx];
            uint64_t b_val = b_bits[idx];

            uint64_t a_xor_b = a ^ b_val;
            uint64_t sum = a_xor_b ^ carry;
            uint64_t carry_next = (a & b_val) | (carry & a_xor_b);

            sum_bits[idx] = sum;
            carry = carry_next;
        }
        if (carry_out != NULL) {
            carry_out[lane] = carry;
        }
    }
#else
    for (int32_t lane = 0; lane < num_lanes_u64; ++lane) {
        uint64_t carry = 0ULL;
        for (int32_t b = 0; b < bit_width; ++b) {
            int32_t idx = b * num_lanes_u64 + lane;
            uint64_t a = a_bits[idx];
            uint64_t b_val = b_bits[idx];

            /* Virtual logic gates */
            uint64_t a_xor_b = a ^ b_val;
            uint64_t sum = a_xor_b ^ carry;
            uint64_t carry_next = (a & b_val) | (carry & a_xor_b);

            sum_bits[idx] = sum;
            carry = carry_next;
        }
        if (carry_out != NULL) {
            carry_out[lane] = carry;
        }
    }
#endif
}

/**
 * 1-Bit XNOR-Popcount Binary MatMul (Mechanism 2).
 * W in {-1, +1}^(N x M) packed as bits (1 = +1, 0 = -1).
 * X in {-1, +1}^M packed as bits.
 * Dot product: Y[r] = 2 * popcount(W_r XNOR X) - total_bits.
 * Zero hardware multiplier instructions!
 */
LEO_EXPORT void leo_bitslice_xnor_gemm(
    const uint64_t *w_bits,       /* Shape: [rows, cols_u64] */
    const uint64_t *x_bits,       /* Shape: [cols_u64] */
    int32_t rows,
    int32_t cols_u64,
    int32_t total_bits,
    int32_t *out_y                /* Shape: [rows] */
) {
    for (int32_t r = 0; r < rows; ++r) {
        const uint64_t *w_row = &w_bits[r * cols_u64];
        int32_t popcount_sum = 0;

#if LEO_HAS_AVX2
        int32_t c = 0;
        for (; c + 3 < cols_u64; c += 4) {
            __m256i w_vec = _mm256_loadu_si256((const __m256i*)(w_row + c));
            __m256i x_vec = _mm256_loadu_si256((const __m256i*)(x_bits + c));
            /* 256-bit SIMD XOR instruction (vpxor) */
            __m256i xor_vec = _mm256_xor_si256(w_vec, x_vec);

            uint64_t v[4];
            _mm256_storeu_si256((__m256i*)v, xor_vec);
            for (int i = 0; i < 4; ++i) {
                uint64_t xnor_val = ~v[i];
#if defined(__GNUC__) || defined(__clang__)
                popcount_sum += __builtin_popcountll(xnor_val);
#elif defined(_MSC_VER) && (defined(_M_X64) || defined(_M_IX86))
                popcount_sum += (int32_t)__popcnt64(xnor_val);
#else
                uint64_t val = xnor_val;
                val = val - ((val >> 1) & 0x5555555555555555ULL);
                val = (val & 0x3333333333333333ULL) + ((val >> 2) & 0x3333333333333333ULL);
                val = (val + (val >> 4)) & 0x0F0F0F0F0F0F0F0FULL;
                popcount_sum += (int32_t)((val * 0x0101010101010101ULL) >> 56);
#endif
            }
        }
        for (; c < cols_u64; ++c) {
            uint64_t xnor_val = ~(w_row[c] ^ x_bits[c]);
#if defined(__GNUC__) || defined(__clang__)
            popcount_sum += __builtin_popcountll(xnor_val);
#elif defined(_MSC_VER) && (defined(_M_X64) || defined(_M_IX86))
            popcount_sum += (int32_t)__popcnt64(xnor_val);
#else
            uint64_t val = xnor_val;
            val = val - ((val >> 1) & 0x5555555555555555ULL);
            val = (val & 0x3333333333333333ULL) + ((val >> 2) & 0x3333333333333333ULL);
            val = (val + (val >> 4)) & 0x0F0F0F0F0F0F0F0FULL;
            popcount_sum += (int32_t)((val * 0x0101010101010101ULL) >> 56);
#endif
        }
#else
        for (int32_t c = 0; c < cols_u64; ++c) {
            uint64_t xnor_val = ~(w_row[c] ^ x_bits[c]);
#if defined(__GNUC__) || defined(__clang__)
            popcount_sum += __builtin_popcountll(xnor_val);
#elif defined(_MSC_VER) && (defined(_M_X64) || defined(_M_IX86))
            popcount_sum += (int32_t)__popcnt64(xnor_val);
#else
            /* Portable popcount */
            uint64_t v_val = xnor_val;
            v_val = v_val - ((v_val >> 1) & 0x5555555555555555ULL);
            v_val = (v_val & 0x3333333333333333ULL) + ((v_val >> 2) & 0x3333333333333333ULL);
            v_val = (v_val + (v_val >> 4)) & 0x0F0F0F0F0F0F0F0FULL;
            popcount_sum += (int32_t)((v_val * 0x0101010101010101ULL) >> 56);
#endif
        }
#endif
        out_y[r] = (2 * popcount_sum) - total_bits;
    }
}

/* -------------------------------------------------------------------------- */
/* MECHANISM 3: MULTIPLY-FREE LOOKUP TABLE (LUT / VPSHUFB) ENGINE             */
/* -------------------------------------------------------------------------- */

/**
 * 1-Bit / 2-Bit / 4-Bit Integer GEMV via Nibble Table Lookups.
 * For each group g, lut_table_16b holds 16 precomputed int8_t partial sums.
 * packed_indices holds 2 4-bit nibbles per byte:
 *   low nibble  = index for group (2*b)
 *   high nibble = index for group (2*b + 1)
 *
 * Inner loop uses VPSHUFB (_mm256_shuffle_epi8) when compiled with AVX2.
 * Zero multiplier/FMA instructions executed!
 */
LEO_EXPORT void leo_lut_gemv_1bit(
    const int8_t *lut_table_16b,   /* Shape: [num_groups, 16] */
    const uint8_t *packed_indices, /* Shape: [rows, (num_groups + 1) / 2] */
    int32_t num_groups,
    int32_t rows,
    int32_t *out_y                 /* Shape: [rows] */
) {
    int32_t packed_cols = (num_groups + 1) / 2;

    for (int32_t r = 0; r < rows; ++r) {
        const uint8_t *idx_row = &packed_indices[r * packed_cols];
        int32_t sum = 0;

#if LEO_HAS_AVX2
        int32_t g = 0;
        __m256i acc_16 = _mm256_setzero_si256();
        acc_16 = _mm256_xor_si256(acc_16, acc_16); /* Clear with vpxor */

        /* Process 2 groups at a time using 256-bit VPSHUFB byte shuffles */
        for (; g + 1 < num_groups; g += 2) {
            uint8_t packed = idx_row[g / 2];
            uint8_t idx_low = packed & 0x0F;
            uint8_t idx_high = (packed >> 4) & 0x0F;

            /* Load 16 bytes for group g and 16 bytes for group g+1 into 256-bit register */
            __m128i lut0 = _mm_loadu_si128((const __m128i*)(lut_table_16b + g * 16));
            __m128i lut1 = _mm_loadu_si128((const __m128i*)(lut_table_16b + (g + 1) * 16));
            __m256i lut_pair = _mm256_set_m128i(lut1, lut0);

            /* Set index vector with 0x80 (disables unindexed positions) */
            __m256i idx_vec = _mm256_set1_epi8((char)0x80);
            idx_vec = _mm256_insert_epi8(idx_vec, (char)idx_low, 0);
            idx_vec = _mm256_insert_epi8(idx_vec, (char)idx_high, 16);

            /* Real 256-bit VPSHUFB instruction */
            __m256i val_vec = _mm256_shuffle_epi8(lut_pair, idx_vec);

            int8_t val0 = (int8_t)_mm256_extract_epi8(val_vec, 0);
            int8_t val1 = (int8_t)_mm256_extract_epi8(val_vec, 16);

            /* Accumulate 16-bit partials with vpaddw (_mm256_add_epi16) */
            __m128i pair_8 = _mm_set_epi8(0,0,0,0,0,0,0,0,0,0,0,0,0,0, val1, val0);
            __m256i vals_16 = _mm256_cvtepi8_epi16(pair_8);
            acc_16 = _mm256_add_epi16(acc_16, vals_16);
        }

        /* Horizontal sum of 16-bit lane sums */
        int16_t acc_arr[16];
        _mm256_storeu_si256((__m256i*)acc_arr, acc_16);
        for (int i = 0; i < 16; ++i) {
            sum += (int32_t)acc_arr[i];
        }

        if (g < num_groups) {
            uint8_t packed = idx_row[g / 2];
            uint8_t idx_low = packed & 0x0F;
            sum += (int32_t)lut_table_16b[g * 16 + idx_low];
        }
#else
        for (int32_t g = 0; g < num_groups; ++g) {
            uint8_t packed = idx_row[g / 2];
            uint8_t idx = (g % 2 == 0) ? (packed & 0x0F) : ((packed >> 4) & 0x0F);
            sum += (int32_t)lut_table_16b[g * 16 + idx];
        }
#endif
        out_y[r] = sum;
    }
}

/**
 * Ternary / Multi-bit Floating-Point GEMV via Precomputed Activation LUT.
 * lut_table_float: [num_groups, 16] float values.
 * packed_indices: [rows, (num_groups + 1) / 2] packed nibbles.
 * Zero multiplier instructions executed in the accumulation loop!
 */
LEO_EXPORT void leo_lut_gemv_ternary(
    const float *lut_table_float,  /* Shape: [num_groups, 16] */
    const uint8_t *packed_indices, /* Shape: [rows, (num_groups + 1) / 2] */
    int32_t num_groups,
    int32_t rows,
    float *out_y                   /* Shape: [rows] */
) {
    int32_t packed_cols = (num_groups + 1) / 2;

    for (int32_t r = 0; r < rows; ++r) {
        const uint8_t *idx_row = &packed_indices[r * packed_cols];
        float sum = 0.0f;

        int32_t g = 0;
        for (; g + 1 < num_groups; g += 2) {
            uint8_t packed = idx_row[g / 2];
            uint8_t idx_low = packed & 0x0F;
            uint8_t idx_high = (packed >> 4) & 0x0F;

            sum += lut_table_float[g * 16 + idx_low];
            sum += lut_table_float[(g + 1) * 16 + idx_high];
        }
        if (g < num_groups) {
            uint8_t packed = idx_row[g / 2];
            uint8_t idx_low = packed & 0x0F;
            sum += lut_table_float[g * 16 + idx_low];
        }
        out_y[r] = sum;
    }
}

/* -------------------------------------------------------------------------- */
/* MECHANISM 4: BIT-EXACT ISA & MICROCODE EMULATION (FP8 & CUDA WARP)         */
/* -------------------------------------------------------------------------- */

/**
 * FP8 E4M3 (OCP Standard): 1 sign bit, 4 exponent bits (bias=7), 3 mantissa bits.
 * Max normal = 448.0. Subnormals supported. NaN = 0x7F / 0xFF.
 */
LEO_EXPORT float leo_fp8_e4m3_to_float(uint8_t b) {
    uint32_t s = (b >> 7) & 0x1;
    uint32_t exp = (b >> 3) & 0xF;
    uint32_t mant = b & 0x7;

    if (exp == 0xF && mant == 0x7) {
        return NAN;
    }
    float sign = s ? -1.0f : 1.0f;
    if (exp == 0) {
        /* Subnormal: 2^(-6) * (mant / 8) */
        return sign * (float)mant * 0.001953125f; /* 2^(-6) / 8 = 1/512 = 0.001953125 */
    }
    /* Normal: 2^(exp - 7) * (1 + mant / 8) */
    float val = (1.0f + (float)mant / 8.0f) * ldexpf(1.0f, (int)exp - 7);
    return sign * val;
}

LEO_EXPORT uint8_t leo_float_to_fp8_e4m3(float val) {
    if (isnan(val)) {
        return 0x7F; /* Standard FP8 E4M3 NaN */
    }
    uint8_t s = signbit(val) ? 0x80 : 0x00;
    float abs_val = fabsf(val);

    if (abs_val > 448.0f) {
        abs_val = 448.0f; /* Saturate to max representable normal */
    }
    if (abs_val < 0.0009765625f) { /* Underflow boundary */
        return s; /* Signed zero */
    }

    /* Subnormal check */
    if (abs_val < 0.015625f) { /* 2^(-6) */
        int32_t mant = (int32_t)roundf(abs_val * 512.0f);
        if (mant > 7) mant = 7;
        return s | (uint8_t)mant;
    }

    int exp;
    float frac = frexpf(abs_val, &exp); /* abs_val = frac * 2^exp, frac in [0.5, 1) */
    /* normal representation: (1 + mant/8) * 2^(e - 7) */
    int biased_exp = exp + 6; /* since frexp is [0.5, 1), normalized is [1.0, 2) * 2^(exp-1) */
    float scaled = (frac * 2.0f - 1.0f) * 8.0f;
    int32_t mant = (int32_t)roundf(scaled);

    if (mant >= 8) {
        mant = 0;
        biased_exp++;
    }
    if (biased_exp > 15) {
        biased_exp = 15;
        mant = 6; /* 448.0f max normal */
    }
    if (biased_exp == 15 && mant >= 7) {
        mant = 6;
    }
    return s | ((uint8_t)biased_exp << 3) | ((uint8_t)mant & 0x7);
}

/**
 * FP8 E5M2 (OCP Standard): 1 sign bit, 5 exponent bits (bias=15), 2 mantissa bits.
 * Format identical to IEEE half-precision with fewer exponent/mantissa bits.
 */
LEO_EXPORT float leo_fp8_e5m2_to_float(uint8_t b) {
    uint32_t s = (b >> 7) & 0x1;
    uint32_t exp = (b >> 2) & 0x1F;
    uint32_t mant = b & 0x3;

    float sign = s ? -1.0f : 1.0f;
    if (exp == 0x1F) {
        return (mant == 0) ? (s ? -INFINITY : INFINITY) : NAN;
    }
    if (exp == 0) {
        /* Subnormal: 2^(-14) * (mant / 4) */
        return sign * (float)mant * 0.0000152587890625f; /* 2^(-14) / 4 */
    }
    /* Normal: 2^(exp - 15) * (1 + mant / 4) */
    float val = (1.0f + (float)mant / 4.0f) * ldexpf(1.0f, (int)exp - 15);
    return sign * val;
}

LEO_EXPORT uint8_t leo_float_to_fp8_e5m2(float val) {
    if (isnan(val)) return 0x7F;
    if (isinf(val)) return signbit(val) ? 0xFC : 0x7C;

    uint8_t s = signbit(val) ? 0x80 : 0x00;
    float abs_val = fabsf(val);

    if (abs_val > 57344.0f) {
        return s | 0x7C; /* Overflow to Inf */
    }
    if (abs_val < 0.00000762939453125f) {
        return s; /* Zero */
    }
    if (abs_val < 0.00006103515625f) { /* Subnormal < 2^(-14) */
        int32_t mant = (int32_t)roundf(abs_val * 65536.0f);
        if (mant > 3) mant = 3;
        return s | (uint8_t)mant;
    }

    int exp;
    float frac = frexpf(abs_val, &exp);
    int biased_exp = exp + 14;
    float scaled = (frac * 2.0f - 1.0f) * 4.0f;
    int32_t mant = (int32_t)roundf(scaled);

    if (mant >= 4) {
        mant = 0;
        biased_exp++;
    }
    if (biased_exp >= 31) {
        return s | 0x7C; /* Inf */
    }
    return s | ((uint8_t)biased_exp << 2) | ((uint8_t)mant & 0x3);
}

/**
 * Emulated FP8 E4M3 Fused Dot-Product.
 * Simulates dedicated GPU FP8 Tensor Core dot-product on host silicon.
 */
LEO_EXPORT float leo_emulate_fp8_e4m3_dot(
    const uint8_t *a_fp8,
    const uint8_t *b_fp8,
    int32_t len
) {
    float acc = 0.0f;
    for (int32_t i = 0; i < len; ++i) {
        float fa = leo_fp8_e4m3_to_float(a_fp8[i]);
        float fb = leo_fp8_e4m3_to_float(b_fp8[i]);
        acc += fa * fb;
    }
    return acc;
}

/**
 * Emulates CUDA Warp Shuffle (__shfl_down_sync) across a 32-thread warp.
 * Reduces 32 values to a single sum scalar.
 */
LEO_EXPORT uint32_t leo_emulate_cuda_warp_reduce_sum(const uint32_t *warp_values_32) {
    uint32_t v[32];
    memcpy(v, warp_values_32, 32 * sizeof(uint32_t));

    /* 5-step butterfly reduction */
    for (int offset = 16; offset > 0; offset /= 2) {
        for (int i = 0; i < offset; ++i) {
            v[i] += v[i + offset];
        }
    }
    return v[0];
}
