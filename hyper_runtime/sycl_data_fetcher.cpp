#include <CL/sycl.hpp>
#include <iostream>
#include <vector>

using namespace sycl;

// Pillar 4: SYCL Data Fetcher for the Intel iGPU
// The iGPU acts strictly as a data-movement co-processor, reading 1.58-bit quantized
// weights from RAM and injecting them into the CPU's L3 Cache via streaming hints.

extern "C" void fetch_weights_to_l3(const int8_t* source_ram, int8_t* target_buffer, size_t size_in_bytes) {
    try {
        // Target the Intel UHD iGPU (or default GPU if UHD isn't exclusively matched)
        gpu_selector selector;
        queue q(selector);

        std::cout << "[SYCL] Co-Processor Illusion Engaged on: " 
                  << q.get_device().get_info<info::device::name>() << "\n";

        // Create buffers
        buffer<int8_t, 1> src_buf(source_ram, range<1>(size_in_bytes));
        buffer<int8_t, 1> dst_buf(target_buffer, range<1>(size_in_bytes));

        q.submit([&](handler& h) {
            auto src = src_buf.get_access<access::mode::read>(h);
            auto dst = dst_buf.get_access<access::mode::write>(h);

            h.parallel_for(range<1>(size_in_bytes), [=](id<1> idx) {
                // A standard memory copy executed widely in parallel by the iGPU's Execution Units.
                // In a true driver-level implementation, this would use non-temporal 
                // load/store instructions (_mm_prefetch via intrinsic bridging) 
                // to aggressively dump this into the CPU LLC (Last Level Cache).
                dst[idx] = src[idx];
            });
        });
        q.wait();
        
    } catch (exception const& e) {
        std::cerr << "SYCL Exception: " << e.what() << "\n";
    }
}
