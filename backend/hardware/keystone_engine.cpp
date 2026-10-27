// ==============================================================================
// backend/hardware/keystone_engine.cpp
// Project LEO (HYPER) - Keystone Phase-Transition Implementation
//
// Target: Intel Core i5-12450H (AVX2/FMA) + Intel UHD Graphics (48 EUs)
// Language: C++20
// ==============================================================================

#include "keystone_engine.hpp"

#include <numeric>
#include <random>
#include <algorithm>
#include <cstring>
#include <cstdlib>

#ifdef _WIN32
  #define WIN32_LEAN_AND_MEAN
  #include <windows.h>
#endif

namespace hyper::keystone {

KeystoneEngine::KeystoneEngine() = default;
KeystoneEngine::~KeystoneEngine() = default;

// -----------------------------------------------------------------------------
// 1. Normalized Shannon Entropy Guard
// -----------------------------------------------------------------------------
float KeystoneEngine::compute_normalized_entropy_512(const uint8_t* sample, size_t sample_size) {
    if (!sample || sample_size == 0) return 0.0f;

    uint32_t counts[256] = {0};
    for (size_t i = 0; i < sample_size; ++i) {
        counts[sample[i]]++;
    }

    double entropy = 0.0;
    const double inv_n = 1.0 / static_cast<double>(sample_size);

    for (int b = 0; b < 256; ++b) {
        if (counts[b] > 0) {
            double p = counts[b] * inv_n;
            entropy -= p * (std::log2(p));
        }
    }

    // Normalized to [0.0, 1.0] by dividing by max entropy (8.0 bits for 256 symbols)
    float h_norm = static_cast<float>(entropy / 8.0);
    return std::clamp(h_norm, 0.0f, 1.0f);
}

// -----------------------------------------------------------------------------
// 2. 256-bit AVX2 Hyperdimensional Bitwise VSA Kernel
// -----------------------------------------------------------------------------
uint64_t KeystoneEngine::avx2_vsa_hamming_distance(const uint64_t* vec_a, const uint64_t* vec_b, size_t num_qwords) {
    if (!vec_a || !vec_b || num_qwords == 0) return 0;

    uint64_t total_distance = 0;
    size_t i = 0;

    // Process 4x 64-bit qwords (256 bits) per AVX2 vector iteration
    for (; i + 4 <= num_qwords; i += 4) {
        __m256i va = _mm256_loadu_si256(reinterpret_cast<const __m256i*>(vec_a + i));
        __m256i vb = _mm256_loadu_si256(reinterpret_cast<const __m256i*>(vec_b + i));
        __m256i v_xor = _mm256_xor_si256(va, vb);

        // Extract 64-bit lanes and compute population count via hardware POPCNT
        uint64_t q0 = _mm256_extract_epi64(v_xor, 0);
        uint64_t q1 = _mm256_extract_epi64(v_xor, 1);
        uint64_t q2 = _mm256_extract_epi64(v_xor, 2);
        uint64_t q3 = _mm256_extract_epi64(v_xor, 3);

#if defined(_MSC_VER)
        total_distance += __popcnt64(q0);
        total_distance += __popcnt64(q1);
        total_distance += __popcnt64(q2);
        total_distance += __popcnt64(q3);
#elif defined(__GNUC__) || defined(__clang__)
        total_distance += __builtin_popcountll(q0);
        total_distance += __builtin_popcountll(q1);
        total_distance += __builtin_popcountll(q2);
        total_distance += __builtin_popcountll(q3);
#else
        total_distance += static_cast<uint64_t>(std::popcount(q0) + std::popcount(q1) + std::popcount(q2) + std::popcount(q3));
#endif
    }

    // Scalar tail loop
    for (; i < num_qwords; ++i) {
        uint64_t diff = vec_a[i] ^ vec_b[i];
#if defined(_MSC_VER)
        total_distance += __popcnt64(diff);
#elif defined(__GNUC__) || defined(__clang__)
        total_distance += __builtin_popcountll(diff);
#else
        total_distance += static_cast<uint64_t>(std::popcount(diff));
#endif
    }

    return total_distance;
}

// -----------------------------------------------------------------------------
// 3. Multiplication-Free 1.58-bit Ternary Addition Engine
// -----------------------------------------------------------------------------
void KeystoneEngine::avx2_ternary_matmul(
    const int8_t* W_ternary,
    const float* X,
    float* Out,
    size_t M, size_t K, size_t N
) {
    std::memset(Out, 0, M * N * sizeof(float));

    for (size_t m = 0; m < M; ++m) {
        const int8_t* w_row = W_ternary + m * K;
        float* out_row = Out + m * N;

        for (size_t k = 0; k < K; ++k) {
            int8_t weight = w_row[k];
            if (weight == 0) continue; // Zero weight elimination

            const float* x_row = X + k * N;
            size_t n = 0;

            if (weight == 1) {
                // Vectorized Addition: out_row[n] += x_row[n]
                for (; n + 8 <= N; n += 8) {
                    __m256 v_out = _mm256_loadu_ps(out_row + n);
                    __m256 v_x = _mm256_loadu_ps(x_row + n);
                    _mm256_storeu_ps(out_row + n, _mm256_add_ps(v_out, v_x));
                }
                for (; n < N; ++n) {
                    out_row[n] += x_row[n];
                }
            } else if (weight == -1) {
                // Vectorized Subtraction: out_row[n] -= x_row[n]
                for (; n + 8 <= N; n += 8) {
                    __m256 v_out = _mm256_loadu_ps(out_row + n);
                    __m256 v_x = _mm256_loadu_ps(x_row + n);
                    _mm256_storeu_ps(out_row + n, _mm256_sub_ps(v_out, v_x));
                }
                for (; n < N; ++n) {
                    out_row[n] -= x_row[n];
                }
            }
        }
    }
}

// -----------------------------------------------------------------------------
// 4. Hoare Logic Sparsity Contractor
// -----------------------------------------------------------------------------
SparsityStructure KeystoneEngine::hoare_sparsity_contract(
    const float* matrix,
    size_t rows,
    size_t cols,
    float zero_threshold
) {
    SparsityStructure s;
    s.total_elements = rows * cols;
    s.zero_elements = 0;
    s.is_diagonal = (rows == cols);
    s.is_identity = (rows == cols);
    s.is_constant = true;
    s.constant_value = (s.total_elements > 0) ? matrix[0] : 0.0f;

    std::vector<bool> row_active(rows, false);
    std::vector<bool> col_active(cols, false);

    for (size_t r = 0; r < rows; ++r) {
        for (size_t c = 0; c < cols; ++c) {
            float val = matrix[r * cols + c];
            bool is_zero = (std::abs(val) <= zero_threshold);

            if (is_zero) {
                s.zero_elements++;
            } else {
                row_active[r] = true;
                col_active[c] = true;
            }

            if (val != s.constant_value) {
                s.is_constant = false;
            }

            if (r != c && !is_zero) {
                s.is_diagonal = false;
                s.is_identity = false;
            } else if (r == c && std::abs(val - 1.0f) > zero_threshold) {
                s.is_identity = false;
            }
        }
    }

    s.sparsity_ratio = (s.total_elements > 0)
        ? static_cast<float>(s.zero_elements) / static_cast<float>(s.total_elements)
        : 0.0f;

    for (size_t r = 0; r < rows; ++r) {
        if (row_active[r]) s.active_rows.push_back(static_cast<uint32_t>(r));
    }
    for (size_t c = 0; c < cols; ++c) {
        if (col_active[c]) s.active_cols.push_back(static_cast<uint32_t>(c));
    }

    return s;
}

// -----------------------------------------------------------------------------
// 5. Online Importance Sampling for Matrix Subsumption
// -----------------------------------------------------------------------------
ImportanceSample KeystoneEngine::compute_online_importance_distribution(
    const float* A,
    const float* B,
    size_t M, size_t K, size_t N,
    float target_energy_ratio,
    size_t max_rank
) {
    ImportanceSample result;
    std::vector<float> energy_scores(K, 0.0f);
    double total_energy = 0.0;

    // Calculate column-norm of A and row-norm of B
    for (size_t k = 0; k < K; ++k) {
        double norm_a_sq = 0.0;
        for (size_t m = 0; m < M; ++m) {
            double val = static_cast<double>(A[m * K + k]);
            norm_a_sq += val * val;
        }

        double norm_b_sq = 0.0;
        for (size_t n = 0; n < N; ++n) {
            double val = static_cast<double>(B[k * N + n]);
            norm_b_sq += val * val;
        }

        double score = norm_a_sq * norm_b_sq;
        energy_scores[k] = static_cast<float>(score);
        total_energy += score;
    }

    // Rank indices by energy score
    std::vector<size_t> indices(K);
    std::iota(indices.begin(), indices.end(), 0);
    std::sort(indices.begin(), indices.end(), [&](size_t i1, size_t i2) {
        return energy_scores[i1] > energy_scores[i2];
    });

    double accumulated_energy = 0.0;
    double target_energy = total_energy * target_energy_ratio;
    size_t selected_k = 0;

    for (size_t idx : indices) {
        result.sampled_indices.push_back(idx);
        accumulated_energy += energy_scores[idx];
        selected_k++;
        if (accumulated_energy >= target_energy || selected_k >= max_rank) {
            break;
        }
    }

    result.reduced_dimension = selected_k;
    result.energy_retained = (total_energy > 0) ? static_cast<float>(accumulated_energy / total_energy) : 1.0f;
    return result;
}

// -----------------------------------------------------------------------------
// 6. Zero-Copy Shared Memory Fabric
// -----------------------------------------------------------------------------
void* KeystoneEngine::allocate_zero_copy_shared_memory(size_t bytes_count) {
#ifdef _WIN32
    // VirtualAlloc with PAGE_READWRITE for page-aligned zero-copy access
    void* ptr = VirtualAlloc(NULL, bytes_count, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE);
    return ptr;
#else
    void* ptr = nullptr;
    posix_memalign(&ptr, 4096, bytes_count);
    return ptr;
#endif
}

void KeystoneEngine::free_zero_copy_shared_memory(void* ptr) {
    if (!ptr) return;
#ifdef _WIN32
    VirtualFree(ptr, 0, MEM_RELEASE);
#else
    std::free(ptr);
#endif
}

// -----------------------------------------------------------------------------
// 7. Freivalds O(N^2) Randomized Matrix Verifier
// -----------------------------------------------------------------------------
bool KeystoneEngine::freivalds_verify_gemm(
    const float* A,
    const float* B,
    const float* C,
    size_t M, size_t K, size_t N,
    float epsilon,
    int num_trials
) {
    std::mt19937_64 rng(1337);
    std::uniform_int_distribution<int> dist(0, 1);

    std::vector<float> r(N);
    std::vector<float> Br(K, 0.0f);
    std::vector<float> ABr(M, 0.0f);
    std::vector<float> Cr(M, 0.0f);

    for (int t = 0; t < num_trials; ++t) {
        // Generate Rademacher probe vector r in {-1, +1}^N
        for (size_t j = 0; j < N; ++j) {
            r[j] = dist(rng) ? 1.0f : -1.0f;
        }

        // Compute Br = B * r (O(K * N))
        std::fill(Br.begin(), Br.end(), 0.0f);
        for (size_t k = 0; k < K; ++k) {
            float sum = 0.0f;
            const float* b_row = B + k * N;
            for (size_t j = 0; j < N; ++j) {
                sum += b_row[j] * r[j];
            }
            Br[k] = sum;
        }

        // Compute ABr = A * (B * r) (O(M * K))
        std::fill(ABr.begin(), ABr.end(), 0.0f);
        for (size_t m = 0; m < M; ++m) {
            float sum = 0.0f;
            const float* a_row = A + m * K;
            for (size_t k = 0; k < K; ++k) {
                sum += a_row[k] * Br[k];
            }
            ABr[m] = sum;
        }

        // Compute Cr = C * r (O(M * N))
        std::fill(Cr.begin(), Cr.end(), 0.0f);
        for (size_t m = 0; m < M; ++m) {
            float sum = 0.0f;
            const float* c_row = C + m * N;
            for (size_t j = 0; j < N; ++j) {
                sum += c_row[j] * r[j];
            }
            Cr[m] = sum;
        }

        // Verify ||ABr - Cr||_2 / (||ABr||_2 + 1e-12) <= epsilon
        double diff_norm_sq = 0.0;
        double abr_norm_sq = 0.0;
        for (size_t m = 0; m < M; ++m) {
            double d = static_cast<double>(ABr[m]) - static_cast<double>(Cr[m]);
            double abr_val = static_cast<double>(ABr[m]);
            diff_norm_sq += d * d;
            abr_norm_sq += abr_val * abr_val;
        }

        double relative_diff = std::sqrt(diff_norm_sq) / (std::sqrt(abr_norm_sq) + 1e-12);
        if (relative_diff > epsilon) {
            return false;
        }
    }

    return true;
}

} // namespace hyper::keystone

// -----------------------------------------------------------------------------
// C ABI Export Implementations
// -----------------------------------------------------------------------------
extern "C" {
    KEYSTONE_API float keystone_compute_entropy(const uint8_t* sample, size_t sample_size) {
        return hyper::keystone::KeystoneEngine::compute_normalized_entropy_512(sample, sample_size);
    }

    KEYSTONE_API uint64_t keystone_avx2_vsa_hamming(const uint64_t* a, const uint64_t* b, size_t num_qwords) {
        return hyper::keystone::KeystoneEngine::avx2_vsa_hamming_distance(a, b, num_qwords);
    }

    KEYSTONE_API void* keystone_alloc_zero_copy(size_t bytes) {
        return hyper::keystone::KeystoneEngine::allocate_zero_copy_shared_memory(bytes);
    }

    KEYSTONE_API void keystone_free_zero_copy(void* ptr) {
        hyper::keystone::KeystoneEngine::free_zero_copy_shared_memory(ptr);
    }

    KEYSTONE_API int keystone_freivalds_verify(
        const float* A, const float* B, const float* C,
        size_t M, size_t K, size_t N, float epsilon, int trials
    ) {
        bool ok = hyper::keystone::KeystoneEngine::freivalds_verify_gemm(A, B, C, M, K, N, epsilon, trials);
        return ok ? 1 : 0;
    }

    KEYSTONE_API float leo_evaluate_entropy_avx2(const float* data, size_t count) {
        if (!data || count == 0) return 0.0f;
        size_t total_bytes = count * sizeof(float);
        size_t sample_size = (total_bytes < 512) ? total_bytes : 512;
        return hyper::keystone::KeystoneEngine::compute_normalized_entropy_512(
            reinterpret_cast<const uint8_t*>(data), sample_size
        );
    }

    KEYSTONE_API void leo_execute_vsa_xor_popcnt_avx2(
        const uint64_t* hypervec_A,
        const uint64_t* hypervec_B,
        uint32_t* accumulator,
        size_t bit_count
    ) {
        if (!hypervec_A || !hypervec_B || bit_count == 0) return;
        size_t num_qwords = (bit_count + 63) / 64;
        uint64_t dist = hyper::keystone::KeystoneEngine::avx2_vsa_hamming_distance(hypervec_A, hypervec_B, num_qwords);
        if (accumulator) {
            *accumulator += static_cast<uint32_t>(dist);
        }
    }

    KEYSTONE_API void leo_tmac_ternary_gemv_avx2(
        const uint8_t* packed_2bit_weights,
        const float* row_scales,
        const float* input_vec,
        float* output_vec,
        size_t M,
        size_t K
    ) {
        if (!packed_2bit_weights || !row_scales || !input_vec || !output_vec || M == 0 || K == 0) {
            return;
        }

        static const float LUT_W[4] = {-1.0f, 0.0f, 1.0f, 0.0f};
        const size_t bytes_per_row = (K + 3) / 4;

        for (size_t m = 0; m < M; ++m) {
            const uint8_t* row_bytes = packed_2bit_weights + m * bytes_per_row;
            float scale = row_scales[m];

            __m256 v_acc0 = _mm256_setzero_ps();
            __m256 v_acc1 = _mm256_setzero_ps();

            size_t k = 0;
            size_t b_idx = 0;

            // Process 16 elements (4 bytes) per unrolled AVX2 step
            for (; k + 16 <= K; k += 16, b_idx += 4) {
                uint8_t b0 = row_bytes[b_idx];
                uint8_t b1 = row_bytes[b_idx + 1];
                uint8_t b2 = row_bytes[b_idx + 2];
                uint8_t b3 = row_bytes[b_idx + 3];

                alignas(32) float w_block0[8] = {
                    LUT_W[b0 & 0x03],
                    LUT_W[(b0 >> 2) & 0x03],
                    LUT_W[(b0 >> 4) & 0x03],
                    LUT_W[(b0 >> 6) & 0x03],
                    LUT_W[b1 & 0x03],
                    LUT_W[(b1 >> 2) & 0x03],
                    LUT_W[(b1 >> 4) & 0x03],
                    LUT_W[(b1 >> 6) & 0x03]
                };

                alignas(32) float w_block1[8] = {
                    LUT_W[b2 & 0x03],
                    LUT_W[(b2 >> 2) & 0x03],
                    LUT_W[(b2 >> 4) & 0x03],
                    LUT_W[(b2 >> 6) & 0x03],
                    LUT_W[b3 & 0x03],
                    LUT_W[(b3 >> 2) & 0x03],
                    LUT_W[(b3 >> 4) & 0x03],
                    LUT_W[(b3 >> 6) & 0x03]
                };

                __m256 vw0 = _mm256_load_ps(w_block0);
                __m256 vx0 = _mm256_loadu_ps(input_vec + k);
                v_acc0 = _mm256_fmadd_ps(vw0, vx0, v_acc0);

                __m256 vw1 = _mm256_load_ps(w_block1);
                __m256 vx1 = _mm256_loadu_ps(input_vec + k + 8);
                v_acc1 = _mm256_fmadd_ps(vw1, vx1, v_acc1);
            }

            // Process remaining 8 elements (2 bytes)
            for (; k + 8 <= K; k += 8, b_idx += 2) {
                uint8_t b0 = row_bytes[b_idx];
                uint8_t b1 = row_bytes[b_idx + 1];

                alignas(32) float w_block[8] = {
                    LUT_W[b0 & 0x03],
                    LUT_W[(b0 >> 2) & 0x03],
                    LUT_W[(b0 >> 4) & 0x03],
                    LUT_W[(b0 >> 6) & 0x03],
                    LUT_W[b1 & 0x03],
                    LUT_W[(b1 >> 2) & 0x03],
                    LUT_W[(b1 >> 4) & 0x03],
                    LUT_W[(b1 >> 6) & 0x03]
                };

                __m256 vw = _mm256_load_ps(w_block);
                __m256 vx = _mm256_loadu_ps(input_vec + k);
                v_acc0 = _mm256_fmadd_ps(vw, vx, v_acc0);
            }

            // Horizontal sum of AVX2 accumulators
            __m256 v_sum = _mm256_add_ps(v_acc0, v_acc1);
            alignas(32) float sum_buf[8];
            _mm256_store_ps(sum_buf, v_sum);
            float row_accum = sum_buf[0] + sum_buf[1] + sum_buf[2] + sum_buf[3] +
                              sum_buf[4] + sum_buf[5] + sum_buf[6] + sum_buf[7];

            // Scalar tail loop
            for (; k < K; ++k) {
                size_t byte_pos = k / 4;
                size_t bit_shift = (k % 4) * 2;
                uint8_t code = (row_bytes[byte_pos] >> bit_shift) & 0x03;
                row_accum += LUT_W[code] * input_vec[k];
            }

            output_vec[m] = row_accum * scale;
        }
    }
}
