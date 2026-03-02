#include <iostream>
#include <vector>

extern "C" {
    void block_matrix_multiply_ispc(float* A, float* B, float* C, int M, int N, int K);

    // Provide a generic fallback just in case ISPC isn't compiled
    void fallback_matrix_multiply(float* A, float* B, float* C, int M, int N, int K) {
        for (int i = 0; i < M; ++i) {
            for (int k = 0; k < K; ++k) {
                float a = A[i * K + k];
                #pragma omp simd
                for (int j = 0; j < N; ++j) {
                    C[i * N + j] += a * B[k * N + j];
                }
            }
        }
    }

    void* allocate_aligned_64(size_t size) {
        // Memory-aligned allocation (64-byte alignment typically for AVX512/cache lines)
    #if defined(_WIN32)
        return _aligned_malloc(size, 64);
    #else
        void* ptr = nullptr;
        if (posix_memalign(&ptr, 64, size) != 0) return nullptr;
        return ptr;
    #endif
    }

    void free_aligned(void* ptr) {
    #if defined(_WIN32)
        _aligned_free(ptr);
    #else
        free(ptr);
    #endif
    }
}
