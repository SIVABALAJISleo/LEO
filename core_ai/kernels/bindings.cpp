#include <torch/extension.h>
#include <vector>

// Forward declaration of the AVX2 kernel function
void bitnet_avx2_forward(
    const int16_t* inputs, 
    const int8_t* weights, 
    int32_t* outputs, 
    int batch_size,
    int in_features,
    int out_features);

// Forward declaration of 2:4 sparse AVX2 kernel function
extern "C" void gemm_2_4_sparse_avx2_native(
    const float* inputs,
    const float* W_packed,
    const uint8_t* indices,
    float* outputs,
    int batch_size,
    int in_features,
    int out_features);

// PyTorch wrapper function for BitNet
torch::Tensor bitnet_matmul(torch::Tensor inputs, torch::Tensor weights) {
    TORCH_CHECK(inputs.device().is_cpu(), "inputs must be a CPU tensor");
    TORCH_CHECK(weights.device().is_cpu(), "weights must be a CPU tensor");
    TORCH_CHECK(inputs.dtype() == torch::kInt16, "inputs must be int16");
    TORCH_CHECK(weights.dtype() == torch::kInt8, "weights must be int8 (1.58-bit)");
    
    int batch_size = inputs.size(0);
    int in_features = inputs.size(1);
    int out_features = weights.size(0);
    
    TORCH_CHECK(weights.size(1) == in_features, "input and weight dimensions do not match");

    auto outputs = torch::empty({batch_size, out_features}, torch::dtype(torch::kInt32).device(torch::kCPU));

    const int16_t* inputs_ptr = inputs.data_ptr<int16_t>();
    const int8_t* weights_ptr = weights.data_ptr<int8_t>();
    int32_t* outputs_ptr = outputs.data_ptr<int32_t>();

    bitnet_avx2_forward(inputs_ptr, weights_ptr, outputs_ptr, batch_size, in_features, out_features);

    return outputs;
}

// PyTorch wrapper function for 2:4 Sparse GEMM
torch::Tensor sparse_2_4_matmul(torch::Tensor inputs, torch::Tensor W_packed, torch::Tensor indices) {
    TORCH_CHECK(inputs.device().is_cpu(), "inputs must be a CPU tensor");
    TORCH_CHECK(W_packed.device().is_cpu(), "W_packed must be a CPU tensor");
    TORCH_CHECK(indices.device().is_cpu(), "indices must be a CPU tensor");
    TORCH_CHECK(inputs.dtype() == torch::kFloat32, "inputs must be float32");
    TORCH_CHECK(W_packed.dtype() == torch::kFloat32, "W_packed must be float32");
    TORCH_CHECK(indices.dtype() == torch::kUInt8, "indices must be uint8");

    int batch_size = inputs.size(0);
    int in_features = inputs.size(1);
    int out_features = W_packed.size(0);

    TORCH_CHECK(in_features % 4 == 0, "in_features must be divisible by 4");
    TORCH_CHECK(W_packed.size(1) == in_features / 2, "W_packed dimension mismatch");
    TORCH_CHECK(indices.size(1) == in_features / 4, "indices dimension mismatch");

    auto outputs = torch::empty({batch_size, out_features}, torch::dtype(torch::kFloat32).device(torch::kCPU));

    gemm_2_4_sparse_avx2_native(
        inputs.data_ptr<float>(),
        W_packed.data_ptr<float>(),
        indices.data_ptr<uint8_t>(),
        outputs.data_ptr<float>(),
        batch_size,
        in_features,
        out_features
    );

    return outputs;
}

PYBIND11_MODULE(TORCH_EXTENSION_NAME, m) {
    m.def("bitnet_matmul", &bitnet_matmul, "AVX2 1.58-bit Matrix Multiplication (Pure Add/Sub)");
    m.def("sparse_2_4_matmul", &sparse_2_4_matmul, "AVX2 2:4 Structured Sparse Matrix Multiplication");
}

