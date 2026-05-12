#include <iostream>
#include <vector>
#include <immintrin.h> // AVX2 / AVX512
#include <cstdint>

extern "C" {

// Simplified AVX2 optimized ternary matrix multiplication
// W: weights in {-1, 0, 1} format
// A: activations in INT8
// O: output in INT32
void ternary_gemm_avx2(const int8_t* W, const int8_t* A, int32_t* O, int M, int N, int K) {
    for (int m = 0; m < M; ++m) {
        for (int n = 0; n < N; ++n) {
            __m256i sum_vec = _mm256_setzero_si256();
            int32_t sum = 0;
            int k = 0;
            // Unroll loop for AVX2 (32 bytes at a time)
            for (; k <= K - 32; k += 32) {
                __m256i w_vec = _mm256_loadu_si256((__m256i*)&W[n * K + k]); 
                __m256i a_vec = _mm256_loadu_si256((__m256i*)&A[m * K + k]);
                
                // Multiply W (INT8) and A (INT8)
                __m256i sign_vec = _mm256_sign_epi8(a_vec, w_vec); 
                
                __m256i ones = _mm256_set1_epi8(1);
                __m256i dp = _mm256_maddubs_epi16(sign_vec, ones); // 16-bit sums
                __m256i dp32 = _mm256_madd_epi16(dp, _mm256_set1_epi16(1)); // 32-bit sums
                sum_vec = _mm256_add_epi32(sum_vec, dp32);
            }
            int32_t temp[8];
            _mm256_storeu_si256((__m256i*)temp, sum_vec);
            for(int i=0; i<8; ++i) sum += temp[i];
            
            // Remainder
            for (; k < K; ++k) {
                sum += A[m * K + k] * W[n * K + k];
            }
            O[m * N + n] = sum;
        }
    }
}

} // extern "C"
