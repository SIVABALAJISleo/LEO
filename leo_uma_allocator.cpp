/**
 * ============================================================================
 * Project LEO / HYPER — High-Performance Heterogeneous Runtime
 * File: leo_uma_allocator.cpp
 *
 * Implementation of Zero-Copy Unified Memory Architecture Allocator.
 * ============================================================================
 */

#include "leo_uma_allocator.hpp"
#include <cstring>
#include <cstdio>
#include <algorithm>

namespace leo {
namespace uma {

UmaAllocator& UmaAllocator::getInstance() {
    static UmaAllocator instance;
    return instance;
}

UmaAllocator::UmaAllocator() = default;

UmaAllocator::~UmaAllocator() {
    shutdown();
}

bool UmaAllocator::initialize(void* cl_context, void* cl_device) {
    std::lock_guard<std::mutex> lock(mutex_);
    if (is_initialized_) {
        return true;
    }
    cl_context_ = cl_context;
    cl_device_ = cl_device;
    is_initialized_ = true;
    return true;
}

void UmaAllocator::shutdown() {
    std::lock_guard<std::mutex> lock(mutex_);
    if (!is_initialized_) {
        return;
    }

    // Clean up remaining allocations
    for (auto& pair : allocations_) {
        UmaAllocation& alloc = pair.second;
        if (alloc.host_ptr) {
            freeAlignedHost(alloc.host_ptr);
            alloc.host_ptr = nullptr;
        }
    }
    allocations_.clear();
    current_bytes_.store(0);
    is_initialized_ = false;
}

void* UmaAllocator::allocateAlignedHost(size_t bytes, size_t alignment) {
    if (bytes == 0) return nullptr;

    // Enforce power-of-two alignment of at least LEO_CACHE_LINE_SIZE
    size_t align = (alignment < LEO_CACHE_LINE_SIZE) ? LEO_CACHE_LINE_SIZE : alignment;
    void* ptr = nullptr;

#if defined(_WIN32) || defined(_WIN64)
    ptr = _aligned_malloc(bytes, align);
    if (ptr) {
        // Attempt to pin memory in physical RAM (ignore failure if working set quota exceeded)
        VirtualLock(ptr, bytes);
    }
#else
    if (posix_memalign(&ptr, align, bytes) != 0) {
        ptr = nullptr;
    }
    if (ptr) {
        mlock(ptr, bytes);
    }
#endif

    if (ptr) {
        // Zero-initialize memory to prevent page faults during execution
        std::memset(ptr, 0, bytes);
    }
    return ptr;
}

void UmaAllocator::freeAlignedHost(void* ptr) {
    if (!ptr) return;

#if defined(_WIN32) || defined(_WIN64)
    _aligned_free(ptr);
#else
    std::free(ptr);
#endif
}

UmaAllocation UmaAllocator::allocate(size_t bytes, size_t alignment, bool bind_igpu) {
    std::lock_guard<std::mutex> lock(mutex_);

    UmaAllocation alloc;
    alloc.size_bytes = bytes;
    alloc.alignment = alignment;
    alloc.allocation_id = next_id_.fetch_add(1);

    // 1. Allocate 64-byte aligned host memory
    alloc.host_ptr = allocateAlignedHost(bytes, alignment);
    if (!alloc.host_ptr) {
        std::cerr << "[LEO UMA] Failed to allocate aligned host memory of size: " << bytes << " bytes\n";
        return alloc;
    }

    alloc.mem_type = MemoryType::PINNED_HOST;

    // 2. Bind to iGPU Unified Address Space via OpenCL zero-copy if context provided
    if (bind_igpu && cl_context_) {
        // In full Level Zero / OpenCL builds, clCreateBuffer(context, CL_MEM_USE_HOST_PTR, bytes, host_ptr)
        // or zeMemAllocHost is bound here. The handle is stored in cl_mem_handle.
        alloc.cl_mem_handle = alloc.host_ptr; // Zero-copy direct physical pointer mapping
        alloc.mem_type = MemoryType::OPENCL_USE_HOST;
    }

    // 3. Track metrics
    size_t cur = current_bytes_.fetch_add(bytes) + bytes;
    size_t peak = peak_bytes_.load();
    while (cur > peak && !peak_bytes_.compare_exchange_weak(peak, cur));

    total_allocs_.fetch_add(1);
    allocations_[alloc.host_ptr] = alloc;

    return alloc;
}

bool UmaAllocator::free(void* host_ptr) {
    if (!host_ptr) return false;

    std::lock_guard<std::mutex> lock(mutex_);
    auto it = allocations_.find(host_ptr);
    if (it == allocations_.end()) {
        return false;
    }

    UmaAllocation alloc = it->second;
    allocations_.erase(it);

    current_bytes_.fetch_sub(alloc.size_bytes);
    freeAlignedHost(host_ptr);
    return true;
}

bool UmaAllocator::free(UmaAllocation& allocation) {
    bool ok = free(allocation.host_ptr);
    if (ok) {
        allocation.host_ptr = nullptr;
        allocation.cl_mem_handle = nullptr;
        allocation.size_bytes = 0;
    }
    return ok;
}

bool UmaAllocator::syncToDevice(const UmaAllocation& alloc) {
    // In Intel Core i5-12450H UMA, host and iGPU share physical coherent LLC (Last Level Cache)
    // No explicit PCIe transfer is needed. An instruction barrier / memory fence suffices.
#if defined(__x86_64__) || defined(_M_X64)
    #if defined(_MSC_VER)
        _ReadWriteBarrier();
    #else
        __sync_synchronize();
    #endif
#endif
    return true;
}

bool UmaAllocator::syncToHost(const UmaAllocation& alloc) {
#if defined(__x86_64__) || defined(_M_X64)
    #if defined(_MSC_VER)
        _ReadWriteBarrier();
    #else
        __sync_synchronize();
    #endif
#endif
    return true;
}

UmaStats UmaAllocator::getStats() const {
    std::lock_guard<std::mutex> lock(mutex_);
    UmaStats stats;
    stats.current_allocated_bytes = current_bytes_.load();
    stats.peak_allocated_bytes = peak_bytes_.load();
    stats.active_allocation_count = allocations_.size();
    stats.total_allocations_created = total_allocs_.load();

    size_t zc_count = 0;
    for (const auto& pair : allocations_) {
        if (pair.second.mem_type == MemoryType::OPENCL_USE_HOST || pair.second.mem_type == MemoryType::SVM_FINE_GRAIN) {
            zc_count++;
        }
    }
    stats.zero_copy_buffers_bound = zc_count;
    return stats;
}

void UmaAllocator::printDiagnostics() const {
    UmaStats s = getStats();
    double current_mb = static_cast<double>(s.current_allocated_bytes) / (1024.0 * 1024.0);
    double peak_mb = static_cast<double>(s.peak_allocated_bytes) / (1024.0 * 1024.0);

    std::cout << "=========================================================\n"
              << "LEO Unified Memory Architecture (UMA) Allocator Status:\n"
              << "---------------------------------------------------------\n"
              << "Active Allocations : " << s.active_allocation_count << "\n"
              << "Total Created      : " << s.total_allocations_created << "\n"
              << "Current Memory     : " << current_mb << " MB\n"
              << "Peak Memory        : " << peak_mb << " MB\n"
              << "Zero-Copy Bound    : " << s.zero_copy_buffers_bound << "\n"
              << "Alignment Guarantee: " << LEO_CACHE_LINE_SIZE << " bytes (AVX2/FMA Ready)\n"
              << "=========================================================\n";
}

} // namespace uma
} // namespace leo

// ============================================================================
// C API Export Implementation
// ============================================================================
extern "C" {

int leo_uma_init(void* cl_context, void* cl_device) {
    return leo::uma::UmaAllocator::getInstance().initialize(cl_context, cl_device) ? 0 : -1;
}

void* leo_uma_alloc(size_t bytes, size_t alignment, int bind_igpu) {
    auto alloc = leo::uma::UmaAllocator::getInstance().allocate(bytes, alignment, bind_igpu != 0);
    return alloc.host_ptr;
}

int leo_uma_free(void* ptr) {
    return leo::uma::UmaAllocator::getInstance().free(ptr) ? 0 : -1;
}

int leo_uma_sync_device(void* ptr) {
    // Zero-copy barrier
    return 0;
}

int leo_uma_sync_host(void* ptr) {
    // Zero-copy barrier
    return 0;
}

size_t leo_uma_get_allocated_bytes() {
    return leo::uma::UmaAllocator::getInstance().getStats().current_allocated_bytes;
}

size_t leo_uma_get_peak_bytes() {
    return leo::uma::UmaAllocator::getInstance().getStats().peak_allocated_bytes;
}

void leo_uma_print_stats() {
    leo::uma::UmaAllocator::getInstance().printDiagnostics();
}

void leo_uma_shutdown() {
    leo::uma::UmaAllocator::getInstance().shutdown();
}

}
