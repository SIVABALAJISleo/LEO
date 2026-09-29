/**
 * PROJECT LEO / HYPER: C++ NATIVE ACCELERATION BACKEND
 * FILE: kernels/usm/hyper_usm_scheduler.hpp
 * 
 * Zero-Copy Heterogeneous Unified Shared Memory (USM) Scheduler
 * Target: Intel Core i5-12450H (4 P-cores, 4 E-cores), Intel UHD Graphics (48 EUs), Windows 11.
 * 
 * Features:
 * 1. Zero-Copy Shared Virtual Memory allocation across Host CPU and iGPU.
 * 2. Hardware-specific thread pinning:
 *    - 4 Golden Cove P-cores (Affinity 0x0F): VSA bit folding & AVX2 popcount reduction.
 *    - 4 Gracemont E-cores (Affinity 0xF0): Background paging, cache eviction, prefetch.
 * 3. Raw pointer submission to 48 iGPU Execution Units without PCIe host-device copies.
 */

#pragma once

#ifndef HYPER_USM_SCHEDULER_HPP
#define HYPER_USM_SCHEDULER_HPP

#include <cstddef>
#include <cstdint>
#include <atomic>
#include <mutex>
#include <unordered_map>

#define USM_CACHE_LINE_ALIGNMENT 64

#if defined(_MSC_VER)
    #define USM_EXPORT __declspec(dllexport)
    #define USM_INLINE __forceinline
    #define USM_RESTRICT __restrict
#else
    #define USM_EXPORT __attribute__((visibility("default")))
    #define USM_INLINE inline __attribute__((always_inline))
    #define USM_RESTRICT __restrict__
#endif

namespace hyper::usm {

enum class USMMemoryType {
    PINNED_HOST_SVM,       // Shared Virtual Memory accessible via single virtual pointer
    ALIGNED_CACHE_HOST,    // 64-byte aligned for AVX2 P-core execution
    DEVICE_LOCAL_ZERO_COPY // iGPU mapped zero-copy buffer
};

struct USMBufferDescriptor {
    void* raw_ptr = nullptr;
    size_t size_bytes = 0;
    USMMemoryType mem_type = USMMemoryType::PINNED_HOST_SVM;
    bool is_gpu_accessible = false;
};

extern "C" {

/**
 * Initializes the heterogeneous USM runtime.
 */
USM_EXPORT int usm_runtime_init();

/**
 * Shuts down the USM runtime and releases tracked memory handles.
 */
USM_EXPORT void usm_runtime_shutdown();

/**
 * Allocates 64-byte cacheline-aligned unified memory accessible by both
 * Host CPU and Intel UHD iGPU without copying.
 */
USM_EXPORT void* usm_allocate_shared(size_t size_bytes, size_t alignment);

/**
 * Frees a shared USM memory buffer.
 */
USM_EXPORT void usm_free_shared(void* ptr);

/**
 * Pins calling thread to the 4 Golden Cove P-Cores (Logical Processors 0..3).
 * Used for latency-critical AVX2 VSA folding and popcount reduction.
 */
USM_EXPORT int usm_pin_to_pcores();

/**
 * Pins calling thread to the 4 Gracemont E-Cores (Logical Processors 4..7).
 * Used for asynchronous paging, cache maintenance, and background tasks.
 */
USM_EXPORT int usm_pin_to_ecores();

/**
 * Executes a zero-copy bitwise boolean mask kernel over an in-place USM buffer.
 * Bypasses PCIe transfer entirely by directly referencing shared host-device pointer.
 */
USM_EXPORT void usm_igpu_apply_boolean_mask(
    uint32_t* USM_RESTRICT target_usm_buffer,
    const uint32_t* USM_RESTRICT mask_usm_buffer,
    size_t num_u32_words
);

/**
 * Returns total active USM bytes currently allocated.
 */
USM_EXPORT size_t usm_get_allocated_bytes();

} // extern "C"

} // namespace hyper::usm

#endif // HYPER_USM_SCHEDULER_HPP
