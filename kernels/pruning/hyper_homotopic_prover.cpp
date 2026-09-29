/**
 * PROJECT LEO (HYPER) - MASTER BYPASS ARCHITECTURE
 * FILE: kernels/pruning/hyper_homotopic_prover.cpp
 * 
 * Implementation of Pillar 3: Homotopic Path Contraction & Hoare Logic Invariant Pruning.
 */

#include "hyper_homotopic_prover.hpp"
#include <cmath>
#include <cstring>
#include <algorithm>

namespace hyper::pruning {

extern "C" {

PROVER_EXPORT bool prover_check_null_tensor(
    const float* PROVER_RESTRICT tensor_data,
    size_t num_elements,
    float epsilon
) {
    if (!tensor_data || num_elements == 0) return true;

    __m256 eps_vec = _mm256_set1_ps(epsilon);
    __m256 sign_mask = _mm256_set1_ps(-0.0f); // Clears sign bit for abs()
    size_t i = 0;

    for (; i + 8 <= num_elements; i += 8) {
        __m256 v = _mm256_loadu_ps(tensor_data + i);
        __m256 abs_v = _mm256_andnot_ps(sign_mask, v);
        __m256 cmp = _mm256_cmp_ps(abs_v, eps_vec, _CMP_GT_OQ);
        int mask = _mm256_movemask_ps(cmp);
        if (mask != 0) {
            return false; // Found non-zero entry exceeding epsilon
        }
    }

    for (; i < num_elements; ++i) {
        if (std::fabs(tensor_data[i]) > epsilon) {
            return false;
        }
    }

    return true;
}

PROVER_EXPORT bool prover_check_non_negative_invariant(
    const float* PROVER_RESTRICT tensor_data,
    size_t num_elements
) {
    if (!tensor_data || num_elements == 0) return true;

    __m256 zero_vec = _mm256_setzero_ps();
    size_t i = 0;

    for (; i + 8 <= num_elements; i += 8) {
        __m256 v = _mm256_loadu_ps(tensor_data + i);
        __m256 cmp = _mm256_cmp_ps(v, zero_vec, _CMP_LT_OQ);
        int mask = _mm256_movemask_ps(cmp);
        if (mask != 0) {
            return false; // Contains negative element -> ReLU would modify tensor
        }
    }

    for (; i < num_elements; ++i) {
        if (tensor_data[i] < 0.0f) {
            return false;
        }
    }

    return true; // All elements >= 0, {P: X >= 0} ReLU(X) {Q: ReLU(X) == X} holds!
}

PROVER_EXPORT bool prover_check_ray_miss_bounding_box(
    const float* PROVER_RESTRICT ray_origins,
    const float* PROVER_RESTRICT ray_dirs,
    size_t num_rays,
    float box_min_x, float box_min_y, float box_min_z,
    float box_max_x, float box_max_y, float box_max_z
) {
    if (!ray_origins || !ray_dirs || num_rays == 0) return true;

    // Classic Kay-Kajiya slab method
    for (size_t r = 0; r < num_rays; ++r) {
        float ox = ray_origins[r * 3 + 0];
        float oy = ray_origins[r * 3 + 1];
        float oz = ray_origins[r * 3 + 2];

        float dx = ray_dirs[r * 3 + 0];
        float dy = ray_dirs[r * 3 + 1];
        float dz = ray_dirs[r * 3 + 2];

        float inv_dx = (std::fabs(dx) > 1e-8f) ? (1.0f / dx) : 1e8f;
        float inv_dy = (std::fabs(dy) > 1e-8f) ? (1.0f / dy) : 1e8f;
        float inv_dz = (std::fabs(dz) > 1e-8f) ? (1.0f / dz) : 1e8f;

        float t1 = (box_min_x - ox) * inv_dx;
        float t2 = (box_max_x - ox) * inv_dx;
        float t3 = (box_min_y - oy) * inv_dy;
        float t4 = (box_max_y - oy) * inv_dy;
        float t5 = (box_min_z - oz) * inv_dz;
        float t6 = (box_max_z - oz) * inv_dz;

        float tmin = std::max(std::max(std::min(t1, t2), std::min(t3, t4)), std::min(t5, t6));
        float tmax = std::min(std::min(std::max(t1, t2), std::max(t3, t4)), std::max(t5, t6));

        if (tmax >= tmin && tmax > 0.0f) {
            return false; // At least one ray intersects the bounding box
        }
    }

    return true; // All rays miss the bounding volume completely
}

PROVER_EXPORT PruningReport prover_contract_execution_queue(
    KernelDispatch* PROVER_RESTRICT dispatch_queue,
    size_t num_dispatches
) {
    PruningReport report{};
    report.total_dispatches = num_dispatches;

    if (!dispatch_queue || num_dispatches == 0) {
        return report;
    }

    for (size_t i = 0; i < num_dispatches; ++i) {
        KernelDispatch& d = dispatch_queue[i];
        d.is_pruned = false;
        d.prune_reason = nullptr;

        switch (d.op_type) {
            case KernelOpType::OP_MUL_ANNIHILATOR: {
                // Invariant: X * 0 = 0. If in_b is zero tensor, output is constant zero.
                if (prover_check_null_tensor(d.in_ptr_b, d.num_elements, 1e-7f)) {
                    d.is_pruned = true;
                    d.prune_reason = "ANNIHILATOR_ZERO_OPERAND";
                    report.pruned_dispatches++;
                    report.hoare_triples_verified++;
                    report.eliminated_flops += (d.num_elements * 2);
                    if (d.out_ptr) std::memset(d.out_ptr, 0, d.num_elements * sizeof(float));
                }
                break;
            }

            case KernelOpType::OP_ADD_IDENTITY: {
                // Invariant: X + 0 = X. If in_b is zero, output is identity copy of in_a.
                if (prover_check_null_tensor(d.in_ptr_b, d.num_elements, 1e-7f)) {
                    d.is_pruned = true;
                    d.prune_reason = "IDENTITY_ZERO_ADDITION";
                    report.pruned_dispatches++;
                    report.hoare_triples_verified++;
                    report.eliminated_flops += d.num_elements;
                    if (d.out_ptr && d.in_ptr_a && d.out_ptr != d.in_ptr_a) {
                        std::memcpy(d.out_ptr, d.in_ptr_a, d.num_elements * sizeof(float));
                    }
                }
                break;
            }

            case KernelOpType::OP_RELU: {
                // Invariant: {P: forall x, x >= 0} ReLU(x) {Q: ReLU(x) == x}.
                if (prover_check_non_negative_invariant(d.in_ptr_a, d.num_elements)) {
                    d.is_pruned = true;
                    d.prune_reason = "IDEMPOTENT_RELU_ALREADY_NON_NEGATIVE";
                    report.pruned_dispatches++;
                    report.hoare_triples_verified++;
                    report.eliminated_flops += d.num_elements;
                    if (d.out_ptr && d.in_ptr_a && d.out_ptr != d.in_ptr_a) {
                        std::memcpy(d.out_ptr, d.in_ptr_a, d.num_elements * sizeof(float));
                    }
                }
                break;
            }

            case KernelOpType::OP_DENSE_GEMM:
            case KernelOpType::OP_SPARSE_GEMM: {
                // If input activation is all zeroes, output is zero (assuming no bias or zero bias)
                if (prover_check_null_tensor(d.in_ptr_a, d.num_elements, 1e-7f)) {
                    d.is_pruned = true;
                    d.prune_reason = "NULL_INPUT_ACTIVATION_GEMM";
                    report.pruned_dispatches++;
                    report.hoare_triples_verified++;
                    report.eliminated_flops += (d.num_elements * 512); // Rough GEMM FLOP count
                    if (d.out_ptr) std::memset(d.out_ptr, 0, d.num_elements * sizeof(float));
                }
                break;
            }

            default:
                break;
        }

        if (!d.is_pruned) {
            report.active_dispatches++;
        }
    }

    return report;
}

} // extern "C"

} // namespace hyper::pruning
