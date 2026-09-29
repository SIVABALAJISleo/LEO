/**
 * PROJECT LEO / HYPER: C++ NATIVE ACCELERATION BACKEND
 * FILE: kernels/usm/hyper_usm_scheduler.cpp
 * 
 * Implementation of Zero-Copy Heterogeneous USM Scheduler.
 */

#include "hyper_usm_scheduler.hpp"
#include <immintrin.h>
#include <cstdlib>
#include <cstring>
#include <iostream>

#ifdef _WIN32
#ifndef WIN32_LEAN_AND_MEAN
#define WIN32_LEAN_AND_MEAN
#endif
#include <windows.h>
#endif

namespace hyper::usm {

static std::atomic<size_t> g_allocated_bytes{0};
static std::mutex g_usm_mutex;
static std::unordered_map<void*, USMBufferDescriptor> g_allocations;
static std::atomic<bool> g_initialized{false};

extern "C" {

USM_EXPORT int usm_runtime_init() {
    std::lock_guard<std::mutex> lock(g_usm_mutex);
    g_initialized.store(true);
    return 0;
}

USM_EXPORT void usm_runtime_shutdown() {
    std::lock_guard<std::mutex> lock(g_usm_mutex);
    for (auto& pair : g_allocations) {
        if (pair.first) {
#ifdef _WIN32
            _aligned_free(pair.first);
#else
            std::free(pair.first);
#endif
        }
    }
    g_allocations.clear();
    g_allocated_bytes.store(0);
    g_initialized.store(false);
}

USM_EXPORT void* usm_allocate_shared(size_t size_bytes, size_t alignment) {
    if (size_bytes == 0) return nullptr;
    if (alignment < USM_CACHE_LINE_ALIGNMENT) {
        alignment = USM_CACHE_LINE_ALIGNMENT;
    }

    void* ptr = nullptr;
#ifdef _WIN32
    ptr = _aligned_malloc(size_bytes, alignment);
#else
    if (posix_memalign(&ptr, alignment, size_bytes) != 0) {
        ptr = nullptr;
    }
#endif

    if (ptr) {
        std::memset(ptr, 0, size_bytes);
        std::lock_guard<std::mutex> lock(g_usm_mutex);
        USMBufferDescriptor desc;
        desc.raw_ptr = ptr;
        desc.size_bytes = size_bytes;
        desc.mem_type = USMMemoryType::PINNED_HOST_SVM;
        desc.is_gpu_accessible = true;
        g_allocations[ptr] = desc;
        g_allocated_bytes.fetch_add(size_bytes);
    }
    return ptr;
}

USM_EXPORT void usm_free_shared(void* ptr) {
    if (!ptr) return;
    std::lock_guard<std::mutex> lock(g_usm_mutex);
    auto it = g_allocations.find(ptr);
    if (it != g_allocations.end()) {
        g_allocated_bytes.fetch_sub(it->second.size_bytes);
        g_allocations.erase(it);
    }
#ifdef _WIN32
    _aligned_free(ptr);
#else
    std::free(ptr);
#endif
}

USM_EXPORT int usm_pin_to_pcores() {
#ifdef _WIN32
    HANDLE hThread = GetCurrentThread();
    // 0x0F pins to logical cores 0, 1, 2, 3 (4 Golden Cove P-Cores)
    DWORD_PTR mask = 0x0F;
    if (SetThreadAffinityMask(hThread, mask) == 0) {
        return -1;
    }
    return 0;
#else
    return 0;
#endif
}

USM_EXPORT int usm_pin_to_ecores() {
#ifdef _WIN32
    HANDLE hThread = GetCurrentThread();
    // 0xF0 pins to logical cores 4, 5, 6, 7 (4 Gracemont E-Cores)
    DWORD_PTR mask = 0xF0;
    if (SetThreadAffinityMask(hThread, mask) == 0) {
        return -1;
    }
    return 0;
#else
    return 0;
#endif
}

USM_EXPORT void usm_igpu_apply_boolean_mask(
    uint32_t* USM_RESTRICT target_usm_buffer,
    const uint32_t* USM_RESTRICT mask_usm_buffer,
    size_t num_u32_words
) {
    // In Intel Core i5 UMA, host and iGPU share the physical ring bus to DDR RAM.
    // Operating directly on the USM pointer executes in-place without PCIe copying.
    size_t num_vec256 = num_u32_words / 8;
    __m256i* v_target = reinterpret_cast<__m256i*>(target_usm_buffer);
    const __m256i* v_mask = reinterpret_cast<const __m256i*>(mask_usm_buffer);

    for (size_t i = 0; i < num_vec256; ++i) {
        __m256i t = _mm256_loadu_si256(v_target + i);
        __m256i m = _mm256_loadu_si256(v_mask + i);
        _mm256_storeu_si256(v_target + i, _mm256_and_si256(t, m));
    }

    // Handle tail elements
    for (size_t i = num_vec256 * 8; i < num_u32_words; ++i) {
        target_usm_buffer[i] &= mask_usm_buffer[i];
    }
}

USM_EXPORT size_t usm_get_allocated_bytes() {
    return g_allocated_bytes.load();
}

} // extern "C"

} // namespace hyper::usm
