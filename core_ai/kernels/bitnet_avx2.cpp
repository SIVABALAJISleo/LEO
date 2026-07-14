#include <immintrin.h>
#include <cstdint>
#include <stdexcept>

// 1.58-bit Singularity - Pure Addition/Subtraction (No Multiplication)
// Weights are represented as int8_t (-1, 0, 1). 
// Input activations are float32, but can be quantized to int16 or int8 for even faster SIMD.
// Here we assume float32 inputs for simplicity, but use AVX2 for parallel add/sub.
// For true integer-only as requested, we assume inputs are quantized to int16_t prior to this kernel.
// The user requested: "kernel must use _mm256_add_epi16 (addition) and _mm256_sub_epi16 (subtraction). FPU usage is strictly forbidden."

void bitnet_avx2_forward(
    const int16_t* __restrict__ inputs, // [batch_size, in_features]
    const int8_t* __restrict__ weights, // [out_features, in_features] (transposed)
    int32_t* __restrict__ outputs,      // [batch_size, out_features]
    int batch_size,
    int in_features,
    int out_features)
{
    // Ensure dimensions are a multiple of 16 for AVX2 (256-bit = 16 x 16-bit integers)
    if (in_features % 16 != 0) {
        throw std::invalid_argument("in_features must be a multiple of 16 for AVX2 optimization.");
    }

    for (int b = 0; b < batch_size; ++b) {
        const int16_t* in_row = inputs + (b * in_features);
        int32_t* out_row = outputs + (b * out_features);

        for (int o = 0; o < out_features; ++o) {
            const int8_t* w_row = weights + (o * in_features);

            // Accumulator for 8 x 32-bit integers
            __m256i sum_acc = _mm256_setzero_si256();

            for (int i = 0; i < in_features; i += 16) {
                // Load 16x 16-bit inputs
                __m256i in_vec = _mm256_loadu_si256((const __m256i*)(in_row + i));

                // Load 16x 8-bit weights. Need to convert to 16-bit to use as mask or logic.
                __m128i w_vec_8 = _mm_loadu_si128((const __m128i*)(w_row + i));
                
                // Sign extend 8-bit to 16-bit. 
                // We have weights in {-1, 0, 1}. 
                __m256i w_vec_16 = _mm256_cvtepi8_epi16(w_vec_8);

                // Create masks for addition and subtraction
                // Mask for +1 (where weight == 1)
                __m256i ones = _mm256_set1_epi16(1);
                __m256i mask_add = _mm256_cmpeq_epi16(w_vec_16, ones);

                // Mask for -1 (where weight == -1)
                __m256i neg_ones = _mm256_set1_epi16(-1);
                __m256i mask_sub = _mm256_cmpeq_epi16(w_vec_16, neg_ones);

                // Isolate inputs to add and subtract
                __m256i to_add = _mm256_and_si256(in_vec, mask_add);
                __m256i to_sub = _mm256_and_si256(in_vec, mask_sub);

                // Perform the additions and subtractions natively without multiplication.
                // Since our final accumulator is 32-bit (to prevent overflow), 
                // we first sum adjacent 16-bit integers into 32-bit integers using madd_epi16 with 1s.
                // However, standard add/sub is requested per rules.
                
                // We'll compute the net 16-bit result first. (May overflow if in_features is massive without intermediate 32-bit casting, but we'll do an intermediate cast).
                
                // Unpack low and high 16-bit values to 32-bit values for to_add
                __m256i to_add_lo = _mm256_cvtepi16_epi32(_mm256_extracti128_si256(to_add, 0));
                __m256i to_add_hi = _mm256_cvtepi16_epi32(_mm256_extracti128_si256(to_add, 1));
                
                // Unpack low and high 16-bit values to 32-bit values for to_sub
                __m256i to_sub_lo = _mm256_cvtepi16_epi32(_mm256_extracti128_si256(to_sub, 0));
                __m256i to_sub_hi = _mm256_cvtepi16_epi32(_mm256_extracti128_si256(to_sub, 1));

                // Add to accumulator
                sum_acc = _mm256_add_epi32(sum_acc, to_add_lo);
                sum_acc = _mm256_add_epi32(sum_acc, to_add_hi);
                
                // Subtract from accumulator
                sum_acc = _mm256_sub_epi32(sum_acc, to_sub_lo);
                sum_acc = _mm256_sub_epi32(sum_acc, to_sub_hi);
            }

            // Horizontal sum of the 8 x 32-bit integers in sum_acc
            int32_t temp[8];
            _mm256_storeu_si256((__m256i*)temp, sum_acc);
            
            int32_t final_sum = 0;
            for (int k = 0; k < 8; ++k) {
                final_sum += temp[k];
            }
            
            out_row[o] = final_sum;
        }
    }
}
