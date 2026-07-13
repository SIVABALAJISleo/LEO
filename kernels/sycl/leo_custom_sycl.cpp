#include <sycl/sycl.hpp>
#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>

namespace py = pybind11;

// The Silicon Override: Tiled memory-local GEMM optimized for Intel UHD 64-shader execution
void sycl_matmul(py::array_t<float> A, py::array_t<float> B, py::array_t<float> C, int M, int K, int N) {
    py::buffer_info bufA = A.request();
    py::buffer_info bufB = B.request();
    py::buffer_info bufC = C.request();

    float* ptrA = static_cast<float*>(bufA.ptr);
    float* ptrB = static_cast<float*>(bufB.ptr);
    float* ptrC = static_cast<float*>(bufC.ptr);

    try {
        // Force selection of the Intel integrated GPU
        sycl::gpu_selector_v selector;
        sycl::queue q(selector);

        // Tile size matched to UHD shared memory profile
        constexpr int TILE_SIZE = 16; 

        sycl::buffer<float, 2> buf_a(ptrA, sycl::range<2>(M, K));
        sycl::buffer<float, 2> buf_b(ptrB, sycl::range<2>(K, N));
        sycl::buffer<float, 2> buf_c(ptrC, sycl::range<2>(M, N));

        q.submit([&](sycl::handler& h) {
            auto acc_a = buf_a.get_access<sycl::access::mode::read>(h);
            auto acc_b = buf_b.get_access<sycl::access::mode::read>(h);
            auto acc_c = buf_c.get_access<sycl::access::mode::write>(h);

            // Create shared local memory allocated directly on the 64 shaders
            sycl::local_accessor<float, 2> tile_a(sycl::range<2>(TILE_SIZE, TILE_SIZE), h);
            sycl::local_accessor<float, 2> tile_b(sycl::range<2>(TILE_SIZE, TILE_SIZE), h);

            h.parallel_for(sycl::nd_range<2>(
                sycl::range<2>(M, N),
                sycl::range<2>(TILE_SIZE, TILE_SIZE)
            ), [=](sycl::nd_item<2> item) {
                int row = item.get_global_id(0);
                int col = item.get_global_id(1);
                
                int local_row = item.get_local_id(0);
                int local_col = item.get_local_id(1);
                
                float sum = 0.0f;
                
                for (int t = 0; t < K; t += TILE_SIZE) {
                    // Load tile into shared memory
                    tile_a[local_row][local_col] = acc_a[row][t + local_col];
                    tile_b[local_row][local_col] = acc_b[t + local_row][col];
                    
                    item.barrier(sycl::access::fence_space::local_space);
                    
                    for (int k = 0; k < TILE_SIZE; ++k) {
                        sum += tile_a[local_row][k] * tile_b[k][local_col];
                    }
                    
                    item.barrier(sycl::access::fence_space::local_space);
                }
                
                acc_c[row][col] = sum;
            });
        }).wait_and_throw();

    } catch (sycl::exception const& e) {
        std::cerr << "SYCL exception caught: " << e.what() << '\n';
    }
}

PYBIND11_MODULE(leo_sycl_kernels, m) {
    m.doc() = "Leo Silicon Override SYCL Kernels for Intel iGPU";
    m.def("sycl_matmul", &sycl_matmul, "Tiled Matrix Multiplication on Intel iGPU");
}
