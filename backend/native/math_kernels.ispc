export void block_matrix_multiply(uniform float A[], uniform float B[], uniform float C[], uniform int M, uniform int N, uniform int K) {
    // Tiled matrix multiplication for explicit SIMD
    const uniform int tile_size = 16;
    
    for (uniform int i0 = 0; i0 < M; i0 += tile_size) {
        for (uniform int j0 = 0; j0 < N; j0 += tile_size) {
            for (uniform int k0 = 0; k0 < K; k0 += tile_size) {
                
                // ISPC kernel inner loop
                foreach (i = i0 ... min(i0 + tile_size, M)) {
                    for (uniform int k = k0; k < min(k0 + tile_size, K); ++k) {
                        float a = A[i * K + k];
                        foreach (j = j0 ... min(j0 + tile_size, N)) {
                            C[i * N + j] += a * B[k * N + j];
                        }
                    }
                }
                
            }
        }
    }
}
