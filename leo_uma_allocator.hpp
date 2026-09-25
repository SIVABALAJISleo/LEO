/**
 * ============================================================================
 * Project LEO / HYPER — High-Performance Heterogeneous Runtime
 * File: leo_uma_allocator.hpp
 *
 * Module 1: Zero-Copy Unified Memory Architecture (UMA) Allocator
 * Target: Intel Core i5-12450H + Intel UHD Graphics (48 EUs) + 16GB Shared RAM
 *
 * Features:
 * - 64-byte cache-aligned pinned host memory allocation for AVX2 execution.
 * - OpenCL zero-copy host pointer wrapping (CL_MEM_USE_HOST_PTR).
 * - Shared Virtual Memory (SVM) support where available (clSVMAlloc).
 * - Safe RAII abstractions, memory leak tracking, and C ABI exports.
 * ============================================================================
 */

#ifndef LEO_UMA_ALLOCATOR_HPP
#define LEO_UMA_ALLOCATOR_HPP

#include <cstddef>
#include <cstdint>
#include <cstdlib>
#include <atomic>
#include <mutex>
#include <memory>
#include <string>
#include <unordered_map>
#include <iostream>

#if defined(_WIN32) || defined(_WIN64)
    #define LEO_EXPORT __declspec(dllexport)
    #include <windows.h>
    #include <malloc.h>
#else
    #define LEO_EXPORT __attribute__((visibility("default")))
    #include <unistd.h>
    #include <sys/mman.h>
#endif

// Cache line alignment for AVX2 / AVX-512 FMA SIMD vectors
#define LEO_CACHE_LINE_SIZE 64

namespace leo {
namespace uma {

/**
 * Memory type category for hardware routing and buffer lifecycle.
 */
enum class MemoryType {
    PINNED_HOST,       // Pinned 64-byte aligned host memory (P-core AVX2 optimized)
    OPENCL_USE_HOST,   // Zero-copy OpenCL buffer mapped over pinned host RAM
    SVM_FINE_GRAIN,    // Intel Shared Virtual Memory (zero PCIe bus roundtrip)
    STANDARD_ALIGNED   // Standard aligned memory fallback
};

/**
 * Represents a single unified memory allocation handle across CPU and iGPU.
 */
struct UmaAllocation {
    void* host_ptr = nullptr;           // Virtual memory address accessible by CPU
    void* cl_mem_handle = nullptr;      // OpenCL cl_mem or Level Zero ze_image/buffer handle
    size_t size_bytes = 0;              // Total buffer capacity in bytes
    size_t alignment = LEO_CACHE_LINE_SIZE;
    MemoryType mem_type = MemoryType::PINNED_HOST;
    bool is_svm = false;
    bool is_locked = false;
    uint64_t allocation_id = 0;
};

/**
 * Memory usage statistics.
 */
struct UmaStats {
    size_t current_allocated_bytes;
    size_t peak_allocated_bytes;
    size_t active_allocation_count;
    size_t total_allocations_created;
    size_t zero_copy_buffers_bound;
};

/**
 * Thread-safe Zero-Copy Unified Memory Architecture Allocator.
 */
class UmaAllocator {
public:
    static UmaAllocator& getInstance();

    // Lifecycle
    bool initialize(void* cl_context = nullptr, void* cl_device = nullptr);
    void shutdown();

    // Allocation primitives
    UmaAllocation allocate(size_t bytes, size_t alignment = LEO_CACHE_LINE_SIZE, bool bind_igpu = true);
    bool free(void* host_ptr);
    bool free(UmaAllocation& allocation);

    // Memory Synchronization primitives (cache flush/invalidate if non-coherent)
    bool syncToDevice(const UmaAllocation& alloc);
    bool syncToHost(const UmaAllocation& alloc);

    // Diagnostics & stats
    UmaStats getStats() const;
    void printDiagnostics() const;

private:
    UmaAllocator();
    ~UmaAllocator();

    UmaAllocator(const UmaAllocator&) = delete;
    UmaAllocator& operator=(const UmaAllocator&) = delete;

    void* allocateAlignedHost(size_t bytes, size_t alignment);
    void freeAlignedHost(void* ptr);

    mutable std::mutex mutex_;
    bool is_initialized_{false};
    void* cl_context_{nullptr};
    void* cl_device_{nullptr};

    std::atomic<size_t> current_bytes_{0};
    std::atomic<size_t> peak_bytes_{0};
    std::atomic<size_t> total_allocs_{0};
    std::atomic<uint64_t> next_id_{1};

    std::unordered_map<void*, UmaAllocation> allocations_;
};

} // namespace uma
} // namespace leo

// ============================================================================
// C API Export for Dynamic Linking (Python ctypes / cffi)
// ============================================================================
extern "C" {
    LEO_EXPORT int leo_uma_init(void* cl_context, void* cl_device);
    LEO_EXPORT void* leo_uma_alloc(size_t bytes, size_t alignment, int bind_igpu);
    LEO_EXPORT int leo_uma_free(void* ptr);
    LEO_EXPORT int leo_uma_sync_device(void* ptr);
    LEO_EXPORT int leo_uma_sync_host(void* ptr);
    LEO_EXPORT size_t leo_uma_get_allocated_bytes();
    LEO_EXPORT size_t leo_uma_get_peak_bytes();
    LEO_EXPORT void leo_uma_print_stats();
    LEO_EXPORT void leo_uma_shutdown();
}

#endif // LEO_UMA_ALLOCATOR_HPP
