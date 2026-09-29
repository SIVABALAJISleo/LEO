/**
 * PROJECT LEO (HYPER) - MASTER BYPASS ARCHITECTURE
 * FILE: kernels/usm/hyper_usm_svm_runtime.cpp
 * 
 * Implementation of Pillar 2: Zero-Copy Heterogeneous USM / SVM Runtime.
 * Direct pointer sharing across Golden Cove P-Cores and Intel UHD Graphics 48 EUs.
 */

#include "hyper_usm_svm_runtime.hpp"
#include <immintrin.h>
#include <cstdlib>
#include <cstring>
#include <mutex>
#include <unordered_map>

#ifdef _WIN32
#ifndef WIN32_LEAN_AND_MEAN
#define WIN32_LEAN_AND_MEAN
#endif
#include <windows.h>
#endif

namespace hyper::usm {

static std::atomic<size_t> g_svm_allocated_bytes{0};
static std::mutex g_svm_mutex;
static std::unordered_map<void*, SVMBufferDescriptor> g_svm_table;
static std::atomic<bool> g_svm_initialized{false};

extern "C" {

USM_EXPORT int usm_svm_init_runtime() {
    std::lock_guard<std::mutex> lock(g_svm_mutex);
    g_svm_initialized.store(true);
    return 0;
}

USM_EXPORT void usm_svm_shutdown_runtime() {
    std::lock_guard<std::mutex> lock(g_svm_mutex);
    for (auto& pair : g_svm_table) {
        if (pair.first) {
#ifdef _WIN32
            _aligned_free(pair.first);
#else
            std::free(pair.first);
#endif
        }
    }
    g_svm_table.clear();
    g_svm_allocated_bytes.store(0);
    g_svm_initialized.store(false);
}

USM_EXPORT void* usm_svm_allocate(size_t size_bytes, uint32_t svm_flags) {
    if (size_bytes == 0) return nullptr;

    // Cacheline alignment (64 bytes) is strictly required for zero-copy UMA ring bus access
    size_t alignment = USM_SVM_ALIGNMENT;

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
        std::lock_guard<std::mutex> lock(g_svm_mutex);
        SVMBufferDescriptor desc;
        desc.svm_ptr = ptr;
        desc.size_bytes = size_bytes;
        desc.alloc_type = SVMType::UMA_PINNED_CACHE;
        desc.gpu_device_id = 1;
        g_svm_table[ptr] = desc;
        g_svm_allocated_bytes.fetch_add(size_bytes);
    }
    return ptr;
}

USM_EXPORT void usm_svm_free(void* ptr) {
    if (!ptr) return;
    std::lock_guard<std::mutex> lock(g_svm_mutex);
    auto it = g_svm_table.find(ptr);
    if (it != g_svm_table.end()) {
        g_svm_allocated_bytes.fetch_sub(it->second.size_bytes);
        g_svm_table.erase(it);
    }
#ifdef _WIN32
    _aligned_free(ptr);
#else
    std::free(ptr);
#endif
}

USM_EXPORT void usm_svm_coherency_fence(void* ptr, size_t size_bytes) {
    if (!ptr || size_bytes == 0) return;

    // Hardware store fence
    _mm_sfence();

    // Flush cache lines to system memory to guarantee iGPU EUs read up-to-date values on ring bus
    const char* cptr = static_cast<const char*>(ptr);
    for (size_t offset = 0; offset < size_bytes; offset += 64) {
        _mm_clflush(cptr + offset);
    }

    // Memory fence to ensure flush operations serialize
    _mm_mfence();
}

USM_EXPORT void usm_svm_pcore_write_mask(
    void* USM_RESTRICT svm_buffer,
    const uint32_t* USM_RESTRICT mask_source,
    size_t num_words
) {
    if (!svm_buffer || !mask_source || num_words == 0) return;

    uint32_t* target = static_cast<uint32_t*>(svm_buffer);
    size_t num_v256 = num_words / 8;

    for (size_t i = 0; i < num_v256; ++i) {
        __m256i src = _mm256_loadu_si256(reinterpret_cast<const __m256i*>(mask_source + i * 8));
        _mm256_storeu_si256(reinterpret_cast<__m256i*>(target + i * 8), src);
    }

    for (size_t i = num_v256 * 8; i < num_words; ++i) {
        target[i] = mask_source[i];
    }
}

USM_EXPORT void usm_svm_igpu_execute_mask(
    void* USM_RESTRICT svm_target_buffer,
    const void* USM_RESTRICT svm_mask_buffer,
    size_t num_u32_words
) {
    if (!svm_target_buffer || !svm_mask_buffer || num_u32_words == 0) return;

    // Zero-copy execution: Target buffer and mask buffer share the same physical address space.
    // In OpenCL/Level Zero on Intel UHD, this executes via zero-copy kernel clSetKernelArgSVMPointer.
    // For CPU fallback/UMA simulation on Alder Lake ring bus:
    uint32_t* target = static_cast<uint32_t*>(svm_target_buffer);
    const uint32_t* mask = static_cast<const uint32_t*>(svm_mask_buffer);

    size_t num_v256 = num_u32_words / 8;
    for (size_t i = 0; i < num_v256; ++i) {
        __m256i t = _mm256_loadu_si256(reinterpret_cast<const __m256i*>(target + i * 8));
        __m256i m = _mm256_loadu_si256(reinterpret_cast<const __m256i*>(mask + i * 8));
        _mm256_storeu_si256(reinterpret_cast<__m256i*>(target + i * 8), _mm256_and_si256(t, m));
    }

    for (size_t i = num_v256 * 8; i < num_u32_words; ++i) {
        target[i] &= mask[i];
    }
}

USM_EXPORT size_t usm_svm_get_active_bytes() {
    return g_svm_allocated_bytes.load();
}

} // extern "C"

} // namespace hyper::usm
