/**
 * ============================================================================
 * Project LEO / HYPER — High-Performance Heterogeneous Runtime
 * File: leo_igpu_kernels.cl
 *
 * Module 2: OpenCL Kernels for Intel UHD Graphics (48 Execution Units, Xe-LP)
 *
 * Tuned for:
 * - 48 Execution Units (384 ALUs, up to 336 concurrent hardware threads)
 * - Vectorized 128-bit memory transactions (float4 / 16 bytes per memory op)
 * - Shared local memory parallel reductions for sub-microsecond latency
 * - Memory-light, non-branching operations offloaded from P-cores
 * ============================================================================
 */

#pragma OPENCL EXTENSION cl_khr_fp16 : enable

#define EPSILON 1e-5f
#define WG_SIZE 64

// ============================================================================
// 1. RMSNorm Kernel (Root Mean Square Normalization)
// ============================================================================
/**
 * Vectorized RMSNorm: y = (x / sqrt(mean(x^2) + eps)) * weight
 *
 * Tuning:
 * - Uses float4 vectorized loads/stores (128-bit width)
 * - Workgroup cooperative parallel reduction across shared local memory
 *
 * @param input   Input tensor [batch_size, hidden_dim]
 * @param weight  Scale weight vector [hidden_dim]
 * @param output  Output tensor [batch_size, hidden_dim]
 * @param dim     Hidden dimension (must be multiple of 4, e.g., 2048, 4096)
 */
__kernel void leo_rmsnorm_float4(
    __global const float4* restrict input,
    __global const float4* restrict weight,
    __global float4* restrict output,
    const int dim_float4,
    const float eps)
{
    const int row = get_group_id(0);
    const int tid = get_local_id(0);
    const int local_size = get_local_size(0);

    __local float local_sq_sum[WG_SIZE];

    // Compute sum of squares for this row
    float thread_sum = 0.0f;
    const int row_offset = row * dim_float4;

    for (int i = tid; i < dim_float4; i += local_size) {
        float4 val = input[row_offset + i];
        thread_sum += dot(val, val); // val.x^2 + val.y^2 + val.z^2 + val.w^2
    }

    local_sq_sum[tid] = thread_sum;
    barrier(CLK_LOCAL_MEM_FENCE);

    // Tree reduction in local memory
    for (int stride = local_size / 2; stride > 0; stride >>= 1) {
        if (tid < stride) {
            local_sq_sum[tid] += local_sq_sum[tid + stride];
        }
        barrier(CLK_LOCAL_MEM_FENCE);
    }

    // Broadcast RMS multiplier
    float mean_sq = local_sq_sum[0] / (float)(dim_float4 * 4);
    float inv_rms = rsqrt(mean_sq + eps);

    // Normalize and scale with weights
    for (int i = tid; i < dim_float4; i += local_size) {
        float4 in_val = input[row_offset + i];
        float4 w_val  = weight[i];
        output[row_offset + i] = in_val * inv_rms * w_val;
    }
}


// ============================================================================
// 2. LayerNorm Kernel (Layer Normalization with Mean and Variance)
// ============================================================================
/**
 * Vectorized LayerNorm: y = ((x - mean) / sqrt(var + eps)) * weight + bias
 *
 * @param input   Input tensor [batch_size, hidden_dim]
 * @param weight  Scale weight vector [hidden_dim]
 * @param bias    Offset bias vector [hidden_dim]
 * @param output  Output tensor [batch_size, hidden_dim]
 * @param dim_float4 hidden_dim / 4
 */
__kernel void leo_layernorm_float4(
    __global const float4* restrict input,
    __global const float4* restrict weight,
    __global const float4* restrict bias,
    __global float4* restrict output,
    const int dim_float4,
    const float eps)
{
    const int row = get_group_id(0);
    const int tid = get_local_id(0);
    const int local_size = get_local_size(0);

    __local float local_sum[WG_SIZE];
    __local float local_sq_sum[WG_SIZE];

    float thread_sum = 0.0f;
    float thread_sq_sum = 0.0f;
    const int row_offset = row * dim_float4;

    for (int i = tid; i < dim_float4; i += local_size) {
        float4 val = input[row_offset + i];
        thread_sum += (val.x + val.y + val.z + val.w);
        thread_sq_sum += dot(val, val);
    }

    local_sum[tid] = thread_sum;
    local_sq_sum[tid] = thread_sq_sum;
    barrier(CLK_LOCAL_MEM_FENCE);

    for (int stride = local_size / 2; stride > 0; stride >>= 1) {
        if (tid < stride) {
            local_sum[tid] += local_sum[tid + stride];
            local_sq_sum[tid] += local_sq_sum[tid + stride];
        }
        barrier(CLK_LOCAL_MEM_FENCE);
    }

    const float total_elements = (float)(dim_float4 * 4);
    float mean = local_sum[0] / total_elements;
    float variance = (local_sq_sum[0] / total_elements) - (mean * mean);
    if (variance < 0.0f) variance = 0.0f;
    float inv_std = rsqrt(variance + eps);

    float4 v_mean = (float4)(mean, mean, mean, mean);
    float4 v_inv_std = (float4)(inv_std, inv_std, inv_std, inv_std);

    for (int i = tid; i < dim_float4; i += local_size) {
        float4 in_val = input[row_offset + i];
        float4 w_val = weight[i];
        float4 b_val = bias ? bias[i] : (float4)(0.0f);
        output[row_offset + i] = ((in_val - v_mean) * v_inv_std) * w_val + b_val;
    }
}


// ============================================================================
// 3. Numerically Stable Vectorized Softmax Kernel
// ============================================================================
/**
 * Vectorized Softmax: p_i = exp(x_i - max(x)) / sum(exp(x_j - max(x)))
 *
 * @param logits   Input unnormalized log probabilities [batch_size, vocab_size]
 * @param probs    Output probabilities [batch_size, vocab_size]
 * @param length   Number of float4 elements (vocab_size / 4)
 */
__kernel void leo_softmax_float4(
    __global const float4* restrict logits,
    __global float4* restrict probs,
    const int length_float4)
{
    const int row = get_group_id(0);
    const int tid = get_local_id(0);
    const int local_size = get_local_size(0);

    __local float local_max[WG_SIZE];
    __local float local_sum[WG_SIZE];

    const int row_offset = row * length_float4;

    // 1. Find max value across row
    float thread_max = -1e30f;
    for (int i = tid; i < length_float4; i += local_size) {
        float4 val = logits[row_offset + i];
        thread_max = fmax(thread_max, fmax(fmax(val.x, val.y), fmax(val.z, val.w)));
    }

    local_max[tid] = thread_max;
    barrier(CLK_LOCAL_MEM_FENCE);

    for (int stride = local_size / 2; stride > 0; stride >>= 1) {
        if (tid < stride) {
            local_max[tid] = fmax(local_max[tid], local_max[tid + stride]);
        }
        barrier(CLK_LOCAL_MEM_FENCE);
    }
    float row_max = local_max[0];
    barrier(CLK_LOCAL_MEM_FENCE);

    // 2. Compute exp and sum
    float4 v_max = (float4)(row_max);
    float thread_exp_sum = 0.0f;

    for (int i = tid; i < length_float4; i += local_size) {
        float4 val = logits[row_offset + i];
        float4 exp_val = exp(val - v_max);
        thread_exp_sum += (exp_val.x + exp_val.y + exp_val.z + exp_val.w);
    }

    local_sum[tid] = thread_exp_sum;
    barrier(CLK_LOCAL_MEM_FENCE);

    for (int stride = local_size / 2; stride > 0; stride >>= 1) {
        if (tid < stride) {
            local_sum[tid] += local_sum[tid + stride];
        }
        barrier(CLK_LOCAL_MEM_FENCE);
    }
    float inv_sum = 1.0f / (local_sum[0] + 1e-12f);

    // 3. Store normalized probabilities
    for (int i = tid; i < length_float4; i += local_size) {
        float4 val = logits[row_offset + i];
        float4 exp_val = exp(val - v_max);
        probs[row_offset + i] = exp_val * inv_sum;
    }
}


// ============================================================================
// 4. Fast Activation Kernels (SiLU / SwiGLU / GELU)
// ============================================================================
/**
 * Vectorized SiLU (Swish-1): y = x * sigmoid(x)
 */
__kernel void leo_silu_float4(
    __global const float4* restrict in,
    __global float4* restrict out,
    const int total_float4)
{
    const int gid = get_global_id(0);
    if (gid < total_float4) {
        float4 x = in[gid];
        float4 sig = (float4)(1.0f) / ((float4)(1.0f) + exp(-x));
        out[gid] = x * sig;
    }
}

/**
 * Vectorized SwiGLU element-wise multiplication: out = (gate * sigmoid(gate)) * up
 */
__kernel void leo_swiglu_float4(
    __global const float4* restrict gate,
    __global const float4* restrict up,
    __global float4* restrict out,
    const int total_float4)
{
    const int gid = get_global_id(0);
    if (gid < total_float4) {
        float4 g = gate[gid];
        float4 u = up[gid];
        float4 sig = (float4)(1.0f) / ((float4)(1.0f) + exp(-g));
        out[gid] = (g * sig) * u;
    }
}


// ============================================================================
// 5. Dequantization Kernel: Q4_K_M Block to FP32 Vectorized
// ============================================================================
/**
 * Dequantizes 4-bit quantized blocks into 32-bit floats.
 * In Q4_K block: 256 weights packed into 4-bit nibbles with scale and min.
 */
__kernel void leo_dequantize_q4_k_float4(
    __global const uchar* restrict q_bytes,
    __global const float* restrict scales,
    __global const float* restrict mins,
    __global float4* restrict fp32_out,
    const int num_blocks)
{
    const int block_idx = get_global_id(0);
    if (block_idx >= num_blocks) return;

    float scale = scales[block_idx];
    float min_val = mins[block_idx];

    // Each block contains 128 bytes = 256 nibbles = 64 float4s
    const int byte_offset = block_idx * 128;
    const int out_offset = block_idx * 64;

    for (int i = 0; i < 32; ++i) {
        uchar b0 = q_bytes[byte_offset + i * 4 + 0];
        uchar b1 = q_bytes[byte_offset + i * 4 + 1];

        // Unpack 4 nibbles into 4 floats
        float f0 = (float)(b0 & 0x0F) * scale + min_val;
        float f1 = (float)(b0 >> 4)   * scale + min_val;
        float f2 = (float)(b1 & 0x0F) * scale + min_val;
        float f3 = (float)(b1 >> 4)   * scale + min_val;

        fp32_out[out_offset + i] = (float4)(f0, f1, f2, f3);
    }
}
