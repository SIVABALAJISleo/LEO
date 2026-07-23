// OpenCL kernels for binary operations
__kernel void binary_xor_popcnt(
    __global const uint* A,
    __global const uint* B,
    __global uint* C,
    const int num_elements
) {
    int i = get_global_id(0);
    if (i < num_elements) {
        // XNOR logic via XOR and bitwise NOT
        uint xnor_val = ~(A[i] ^ B[i]);
        // POPCNT emulation in OpenCL C (using a common bit-twiddling hack)
        uint count = xnor_val;
        count = count - ((count >> 1) & 0x55555555);
        count = (count & 0x33333333) + ((count >> 2) & 0x33333333);
        count = (((count + (count >> 4)) & 0x0F0F0F0F) * 0x01010101) >> 24;
        C[i] = count;
    }
}
