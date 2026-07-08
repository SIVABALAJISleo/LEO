/**
 * LEO AI V42 - The Irrelevance Engine
 * Phase 5: Local WebAssembly Port (Browser Fallback)
 * 
 * WebGPU Compute Shader for extremely fast 1.58-bit (ternary) matrix multiplication.
 * Allows the browser to utilize the local device's integrated or discrete GPU.
 */

struct MatrixDimensions {
    m: u32, // batch size
    n: u32, // output features
    k: u32, // input features (multiple of 16 for packed format)
};

@group(0) @binding(0) var<uniform> dims: MatrixDimensions;
@group(0) @binding(1) var<storage, read> inputs: array<f32>;        // shape (m, k)
@group(0) @binding(2) var<storage, read> packed_weights: array<u32>; // shape (k/16, n) 2-bit packed
@group(0) @binding(3) var<storage, read_write> outputs: array<f32>;  // shape (m, n)

// Decodes a 2-bit value into a ternary f32 (-1.0, 0.0, 1.0)
fn decode_ternary(packed: u32, index: u32) -> f32 {
    let shift = index * 2u;
    let mask = 3u << shift;
    let val = (packed & mask) >> shift;
    
    // Map: 00 -> 0.0, 01 -> 1.0, 10 -> -1.0, 11 -> 0.0
    if (val == 1u) { return 1.0; }
    if (val == 2u) { return -1.0; }
    return 0.0;
}

const WORKGROUP_SIZE: u32 = 64;

@compute @workgroup_size(WORKGROUP_SIZE, 1, 1)
fn main(@builtin(global_invocation_id) global_id: vec3<u32>) {
    let row = global_id.x / dims.n; // current batch index
    let col = global_id.x % dims.n; // current output feature index

    if (row >= dims.m || col >= dims.n) {
        return;
    }

    var sum: f32 = 0.0;
    let k_packed = dims.k / 16u; // Number of u32s per output feature

    for (var p = 0u; p < k_packed; p = p + 1u) {
        // Fetch the 32-bit packed weight containing 16 ternary values
        let weight_idx = p * dims.n + col;
        let packed_val = packed_weights[weight_idx];

        // Unroll 16 multiplications (avoiding branching where possible in real implementation)
        for (var i = 0u; i < 16u; i = i + 1u) {
            let input_idx = row * dims.k + (p * 16u + i);
            let input_val = inputs[input_idx];
            let w_val = decode_ternary(packed_val, i);
            
            // Add or subtract based on ternary value without standard f32 multiplication
            sum = sum + (input_val * w_val); 
        }
    }

    let out_idx = row * dims.n + col;
    outputs[out_idx] = sum;
}
