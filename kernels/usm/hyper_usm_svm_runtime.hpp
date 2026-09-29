/**
 * PROJECT LEO (HYPER) - MASTER BYPASS ARCHITECTURE
 * FILE: kernels/usm/hyper_usm_svm_runtime.hpp
 * 
 * PILLAR 2: Zero-Copy Heterogeneous Unified Shared Memory (USM / SVM)
 * Hardware Target: Intel Core i5-12450H + Intel UHD Graphics (48 EUs), Windows 11.
 * 
 * Architecture:
 * - Shared Virtual Memory (SVM) via OpenCL clSVMAlloc / Intel Level Zero zeMemAllocShared.
 * - Single physical DRAM allocation on unified ring bus.
 * - P-Cores write binary masks in-place; 48 UHD EUs consume identical pointer with zero PCIe copies.
 */

#pragma once

#ifndef HYPER_USM_SVM_RUNTIME_HPP
#define HYPER_USM_SVM_RUNTIME_HPP

#include <cstdint>
#include <cstddef>
#include <atomic>

#define USM_SVM_ALIGNMENT 64 // Cacheline alignment for Intel Alder Lake CPU/iGPU Ring Bus

#if defined(_MSC_VER)
    #define USM_RESTRICT __restrict
    #define USM_INLINE __forceinline
    #define USM_EXPORT __declspec(dllexport)
#else
    #define USM_RESTRICT __restrict__
    #define USM_INLINE inline __attribute__((always_inline))
    #define USM_EXPORT __attribute__((visibility("default")))
#endif

namespace hyper::usm {

/**
 * SVM Allocation Type
 */
enum class SVMType : uint32_t {
    OPENCL_FINE_GRAIN = 0,    // OpenCL 2.0+ Fine-grained SVM with CPU/GPU atomics
    OPENCL_COARSE_GRAIN = 1,  // OpenCL 2.0+ Coarse-grained SVM
    LEVEL_ZERO_SHARED = 2,    // Intel oneAPI Level Zero zeMemAllocShared
    UMA_PINNED_CACHE = 3      // Fallback 64-byte aligned host-pinned virtual memory
};

/**
 * Descriptor for a zero-copy shared memory region.
 */
struct alignas(USM_SVM_ALIGNMENT) SVMBufferDescriptor {
    void* svm_ptr = nullptr;
    size_t size_bytes = 0;
    SVMType alloc_type = SVMType::UMA_PINNED_CACHE;
    uint32_t gpu_device_id = 0;
    std::atomic<uint32_t> access_fence{0};
};

extern "C" {

/**
 * Initializes the heterogeneous zero-copy USM/SVM runtime.
 * Probes OpenCL / Level Zero driver capabilities for Intel UHD Graphics.
 */
USM_EXPORT int usm_svm_init_runtime();

/**
 * Shuts down the USM runtime and frees tracked shared buffers.
 */
USM_EXPORT void usm_svm_shutdown_runtime();

/**
 * Allocates a zero-copy buffer accessible across both P-Cores and 48 UHD EUs.
 * Guarantees identical 64-bit virtual memory address pointer on both devices.
 */
USM_EXPORT void* usm_svm_allocate(size_t size_bytes, uint32_t svm_flags);

/**
 * Frees a shared virtual memory buffer.
 */
USM_EXPORT void usm_svm_free(void* ptr);

/**
 * Issues a hardware memory fence between P-cores and UHD EUs.
 * Flushes dirty L3/LLC cachelines on Intel Alder Lake ring bus without DMA copying.
 */
USM_EXPORT void usm_svm_coherency_fence(void* ptr, size_t size_bytes);

/**
 * P-Core Parallel In-Place Mask Writer:
 * P-cores (logical cores 0..3) write 10,000-bit binary masks directly to SVM pointer.
 */
USM_EXPORT void usm_svm_pcore_write_mask(
    void* USM_RESTRICT svm_buffer,
    const uint32_t* USM_RESTRICT mask_source,
    size_t num_words
);

/**
 * iGPU In-Place Boolean Mask Kernel:
 * Dispatches parallel reduction to Intel UHD Graphics EUs on the exact same pointer.
 * Zero bytes transferred over PCIe bus.
 */
USM_EXPORT void usm_svm_igpu_execute_mask(
    void* USM_RESTRICT svm_target_buffer,
    const void* USM_RESTRICT svm_mask_buffer,
    size_t num_u32_words
);

/**
 * Returns active total allocated SVM bytes.
 */
USM_EXPORT size_t usm_svm_get_active_bytes();

} // extern "C"

} // namespace hyper::usm

#endif // HYPER_USM_SVM_RUNTIME_HPP
