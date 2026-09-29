/**
 * PROJECT LEO (HYPER) - MASTER BYPASS ARCHITECTURE
 * FILE: kernels/memoization/hyper_l3_memoization.cpp
 * 
 * Implementation of Pillar 4: Semantic L1/L2/L3 Memoization & Irreducible Entropy Fallback.
 * Strictly budgeted to 8.0MB within the 12MB L3 Smart Cache of the Intel Core i5-12450H.
 */

#include "hyper_l3_memoization.hpp"
#include <cmath>
#include <cstring>
#include <cstdlib>
#include <atomic>
#include <mutex>

namespace hyper::memoization {

static L3CacheEntry* g_l3_table = nullptr;
static std::atomic<uint64_t> g_lookups{0};
static std::atomic<uint64_t> g_hits{0};
static std::atomic<uint64_t> g_misses{0};
static std::atomic<uint64_t> g_bypassed_entropy{0};
static std::atomic<uint64_t> g_evictions{0};
static std::mutex g_memo_mutex;

extern "C" {

MEMO_EXPORT int memo_init_table() {
    std::lock_guard<std::mutex> lock(g_memo_mutex);
    if (g_l3_table) return 0;

    size_t total_bytes = L3_MEMO_NUM_ENTRIES * sizeof(L3CacheEntry); // 131072 * 64 = 8,388,608 bytes (8.0 MB)

#ifdef _WIN32
    g_l3_table = static_cast<L3CacheEntry*>(_aligned_malloc(total_bytes, 64));
#else
    if (posix_memalign(reinterpret_cast<void**>(&g_l3_table), 64, total_bytes) != 0) {
        g_l3_table = nullptr;
    }
#endif

    if (!g_l3_table) return -1;

    std::memset(g_l3_table, 0, total_bytes);
    g_lookups.store(0);
    g_hits.store(0);
    g_misses.store(0);
    g_bypassed_entropy.store(0);
    g_evictions.store(0);

    return 0;
}

MEMO_EXPORT void memo_shutdown_table() {
    std::lock_guard<std::mutex> lock(g_memo_mutex);
    if (g_l3_table) {
#ifdef _WIN32
        _aligned_free(g_l3_table);
#else
        std::free(g_l3_table);
#endif
        g_l3_table = nullptr;
    }
}

MEMO_EXPORT bool memo_is_irreducible_entropy(
    const float* MEMO_RESTRICT tensor_data,
    size_t num_elements,
    float threshold
) {
    if (!tensor_data || num_elements < 16) return false;

    // 1. Mean and Variance of tensor elements
    double sum = 0.0;
    double sum_sq = 0.0;
    for (size_t i = 0; i < num_elements; ++i) {
        double v = tensor_data[i];
        sum += v;
        sum_sq += v * v;
    }
    double n = static_cast<double>(num_elements);
    double mean = sum / n;
    double variance = (sum_sq / n) - (mean * mean);

    // If variance is near-zero, it's a constant or near-constant signal (low entropy, compressible)
    if (variance < 1e-9) {
        return false;
    }

    // 2. First-order derivative variance: Var(Delta x) / (2 * Var(x))
    double diff_sum = 0.0;
    double diff_sum_sq = 0.0;
    for (size_t i = 0; i < num_elements - 1; ++i) {
        double d = tensor_data[i + 1] - tensor_data[i];
        diff_sum += d;
        diff_sum_sq += d * d;
    }
    double n_diff = static_cast<double>(num_elements - 1);
    double diff_mean = diff_sum / n_diff;
    double diff_var = (diff_sum_sq / n_diff) - (diff_mean * diff_mean);
    double r_v = diff_var / (2.0 * variance);

    // 3. Wiener Spectral Flatness proxy: Geometric Mean / Arithmetic Mean of energy
    double log_power_sum = 0.0;
    double power_sum = 0.0;
    for (size_t i = 0; i < num_elements; ++i) {
        double p = (tensor_data[i] * tensor_data[i]) + 1e-12;
        power_sum += p;
        log_power_sum += std::log(p);
    }
    double arith_mean = power_sum / n;
    double geom_mean = std::exp(log_power_sum / n);
    double spectral_flatness = (arith_mean > 1e-12) ? (geom_mean / arith_mean) : 0.0;

    // Composite Kolmogorov complexity proxy
    double entropy_score = 0.5 * spectral_flatness + 0.5 * r_v;

    // High entropy (irreducible white noise): bypass cache to avoid polluting 12MB L3
    return (entropy_score >= static_cast<double>(threshold));
}

MEMO_EXPORT uint64_t memo_compute_simhash64(
    const float* MEMO_RESTRICT input_tensor,
    const float* MEMO_RESTRICT hyperplanes,
    size_t in_dim
) {
    if (!input_tensor || !hyperplanes || in_dim == 0) return 0;

    uint64_t hash_key = 0;

    for (size_t p = 0; p < SIMHASH_NUM_PLANES; ++p) {
        const float* plane_weights = hyperplanes + (p * in_dim);
        __m256 acc = _mm256_setzero_ps();
        size_t d = 0;

        for (; d + 8 <= in_dim; d += 8) {
            __m256 x = _mm256_loadu_ps(input_tensor + d);
            __m256 w = _mm256_loadu_ps(plane_weights + d);
            acc = _mm256_fmadd_ps(x, w, acc);
        }

        __m128 lo = _mm256_castps256_ps128(acc);
        __m128 hi = _mm256_extractf128_ps(acc, 1);
        __m128 sum4 = _mm_add_ps(lo, hi);
        sum4 = _mm_hadd_ps(sum4, sum4);
        sum4 = _mm_hadd_ps(sum4, sum4);
        float dot_val = _mm_cvtss_f32(sum4);

        for (; d < in_dim; ++d) {
            dot_val += input_tensor[d] * plane_weights[d];
        }

        if (dot_val > 0.0f) {
            hash_key |= (1ULL << p);
        }
    }

    return hash_key;
}

MEMO_EXPORT int memo_lookup(
    const float* MEMO_RESTRICT input_tensor,
    const float* MEMO_RESTRICT hyperplanes,
    size_t in_dim,
    float* MEMO_RESTRICT out_result,
    size_t out_dim
) {
    g_lookups.fetch_add(1);

    // CRITICAL: IRREDUCIBLE ENTROPY FALLBACK
    // If the input exhibits high Kolmogorov complexity (pure noise), bypass memoization immediately!
    if (memo_is_irreducible_entropy(input_tensor, in_dim, IRREDUCIBLE_ENTROPY_THRESH)) {
        g_bypassed_entropy.fetch_add(1);
        return -1; // Signals caller to execute native path
    }

    if (!g_l3_table) {
        g_misses.fetch_add(1);
        return 0;
    }

    uint64_t key = memo_compute_simhash64(input_tensor, hyperplanes, in_dim);
    size_t index = key & L3_MEMO_INDEX_MASK;
    const L3CacheEntry& entry = g_l3_table[index];

    if (entry.valid == 1 && entry.simhash_key == key) {
        // Cache Hit! Zero FLOP instant retrieval from L3 Smart Cache.
        g_hits.fetch_add(1);
        size_t copy_count = (out_dim < 12) ? out_dim : 12;
        std::memcpy(out_result, entry.output_payload, copy_count * sizeof(float));
        return 1;
    }

    // Cache Miss
    g_misses.fetch_add(1);
    return 0;
}

MEMO_EXPORT void memo_insert(
    uint64_t simhash_key,
    const float* MEMO_RESTRICT output_payload,
    size_t out_dim
) {
    if (!g_l3_table || !output_payload) return;

    size_t index = simhash_key & L3_MEMO_INDEX_MASK;
    L3CacheEntry& entry = g_l3_table[index];

    if (entry.valid == 1) {
        g_evictions.fetch_add(1);
    }

    entry.simhash_key = simhash_key;
    entry.valid = 1;
    entry.tag = static_cast<uint32_t>(simhash_key >> 32);

    size_t copy_count = (out_dim < 12) ? out_dim : 12;
    std::memcpy(entry.output_payload, output_payload, copy_count * sizeof(float));
}

MEMO_EXPORT MemoizationTelemetry memo_get_telemetry() {
    MemoizationTelemetry t{};
    t.lookups = g_lookups.load();
    t.hits = g_hits.load();
    t.misses = g_misses.load();
    t.bypassed_entropy = g_bypassed_entropy.load();
    t.evictions = g_evictions.load();
    t.hit_ratio = (t.lookups > 0) ? (static_cast<float>(t.hits) / static_cast<float>(t.lookups)) : 0.0f;
    return t;
}

} // extern "C"

} // namespace hyper::memoization
