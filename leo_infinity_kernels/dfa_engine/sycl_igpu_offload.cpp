#include <CL/sycl.hpp>
#include <iostream>
#include <vector>

using namespace sycl;

// Simple proof-of-concept for Intel UHD execution of DFA Engine
// Note: This requires Intel oneAPI Base Toolkit and DPC++ compiler (icpx)
extern "C" {
    
    // Perform Trie-Lookup on iGPU
    void dfa_sycl_offload(int8_t* A, int8_t* B, int32_t* C, int M, int K, int N, int16_t* lookup_table) {
        try {
            // Select GPU device
            gpu_selector selector;
            queue q(selector);
            
            std::cout << "Offloading to: " << q.get_device().get_info<info::device::name>() << std::endl;
            
            // Allocate unified shared memory (USM)
            int8_t* A_usm = malloc_shared<int8_t>(M * K, q);
            int8_t* B_usm = malloc_shared<int8_t>(K * N, q);
            int32_t* C_usm = malloc_shared<int32_t>(M * N, q);
            int16_t* table_usm = malloc_shared<int16_t>(256 * 256, q);
            
            // Copy data to USM
            q.memcpy(A_usm, A, M * K * sizeof(int8_t));
            q.memcpy(B_usm, B, K * N * sizeof(int8_t));
            q.memcpy(table_usm, lookup_table, 256 * 256 * sizeof(int16_t));
            q.wait();
            
            // Submit kernel
            q.submit([&](handler& h) {
                h.parallel_for(range<2>(M, N), [=](id<2> index) {
                    int i = index[0];
                    int j = index[1];
                    
                    int32_t sum = 0;
                    for (int k = 0; k < K; ++k) {
                        uint8_t valA = static_cast<uint8_t>(A_usm[i * K + k]);
                        uint8_t valB = static_cast<uint8_t>(B_usm[k * N + j]);
                        sum += table_usm[valA * 256 + valB];
                    }
                    C_usm[i * N + j] = sum;
                });
            }).wait();
            
            // Copy back results
            q.memcpy(C, C_usm, M * N * sizeof(int32_t)).wait();
            
            free(A_usm, q);
            free(B_usm, q);
            free(C_usm, q);
            free(table_usm, q);
            
        } catch (exception const& e) {
            std::cerr << "SYCL exception caught: " << e.what() << '\n';
        }
    }
}
