#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <immintrin.h>
#include <vector>

namespace py = pybind11;

// The DFA Trie-Lookup Table
// Precomputes all possible products of two 8-bit integers (-128 to 127)
static int16_t lookup_table[256 * 256];
static bool table_initialized = false;

void init_lookup_table() {
    if (table_initialized) return;
    for (int i = 0; i < 256; ++i) {
        for (int j = 0; j < 256; ++j) {
            int8_t a = static_cast<int8_t>(i);
            int8_t b = static_cast<int8_t>(j);
            lookup_table[i * 256 + j] = a * b;
        }
    }
    table_initialized = true;
}

py::array_t<int32_t> dfa_gemm_int8(py::array_t<int8_t> a, py::array_t<int8_t> b) {
    init_lookup_table();
    
    auto bufA = a.request();
    auto bufB = b.request();
    
    if (bufA.ndim != 2 || bufB.ndim != 2) {
        throw std::runtime_error("Inputs must be 2D arrays.");
    }
    if (bufA.shape[1] != bufB.shape[0]) {
        throw std::runtime_error("Inner dimensions must match.");
    }
    
    int M = bufA.shape[0];
    int K = bufA.shape[1];
    int N = bufB.shape[1];
    
    auto result = py::array_t<int32_t>({M, N});
    auto bufC = result.request();
    
    int8_t* ptrA = static_cast<int8_t*>(bufA.ptr);
    int8_t* ptrB = static_cast<int8_t*>(bufB.ptr);
    int32_t* ptrC = static_cast<int32_t*>(bufC.ptr);
    
    // Transpose B for better cache locality during AVX accumulation
    std::vector<int8_t> b_t(K * N);
    for(int i=0; i<K; ++i) {
        for(int j=0; j<N; ++j) {
            b_t[j*K + i] = ptrB[i*N + j];
        }
    }
    
    // Simple Trie-Lookup GEMM
    // (AVX2 intrinsics would go here in a fully optimized version, summing the looked-up 16-bit values)
    for (int i = 0; i < M; ++i) {
        for (int j = 0; j < N; ++j) {
            int32_t sum = 0;
            for (int k = 0; k < K; ++k) {
                uint8_t valA = static_cast<uint8_t>(ptrA[i * K + k]);
                uint8_t valB = static_cast<uint8_t>(b_t[j * K + k]);
                sum += lookup_table[valA * 256 + valB];
            }
            ptrC[i * N + j] = sum;
        }
    }
    
    return result;
}

PYBIND11_MODULE(dfa_engine_cpp, m) {
    m.doc() = "DFA Matrix Engine (Trie-Lookup GEMM) for Algorithmic Alchemy";
    m.def("dfa_gemm_int8", &dfa_gemm_int8, "Performs GEMM via lookup table");
}
