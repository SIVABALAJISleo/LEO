/* 
 * Leo Compute WGSL (WebGPU Shading Language)
 * Alternative fallback if SYCL/DPC++ compilation is not available.
 * Computes tiled matrix multiplication on the GPU via Windows Native WebGPU backend.
 */

struct Matrix {
    size: vec2<u32>,
    numbers: array<f32>,
};

@group(0) @binding(0) var<storage, read> firstMatrix : Matrix;
@group(0) @binding(1) var<storage, read> secondMatrix : Matrix;
@group(0) @binding(2) var<storage, read_write> resultMatrix : Matrix;

const TILE_SIZE: u32 = 16u;

var<workgroup> tileA: array<array<f32, TILE_SIZE>, TILE_SIZE>;
var<workgroup> tileB: array<array<f32, TILE_SIZE>, TILE_SIZE>;

@compute @workgroup_size(16, 16)
fn main(
    @builtin(global_invocation_id) global_id : vec3<u32>,
    @builtin(local_invocation_id) local_id : vec3<u32>
) {
    let row = global_id.x;
    let col = global_id.y;
    
    let local_row = local_id.x;
    let local_col = local_id.y;
    
    let K = firstMatrix.size.y;
    var sum: f32 = 0.0;
    
    for (var t: u32 = 0u; t < K; t = t + TILE_SIZE) {
        // Load into shared memory
        tileA[local_row][local_col] = firstMatrix.numbers[row * K + (t + local_col)];
        tileB[local_row][local_col] = secondMatrix.numbers[(t + local_row) * secondMatrix.size.y + col];
        
        workgroupBarrier();
        
        for (var k: u32 = 0u; k < TILE_SIZE; k = k + 1u) {
            sum = sum + tileA[local_row][k] * tileB[k][local_col];
        }
        
        workgroupBarrier();
    }
    
    resultMatrix.numbers[row * resultMatrix.size.y + col] = sum;
}
