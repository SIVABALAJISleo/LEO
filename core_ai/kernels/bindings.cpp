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

// PyTorch wrapper function
torch::Tensor bitnet_matmul(torch::Tensor inputs, torch::Tensor weights) {
    TORCH_CHECK(inputs.device().is_cpu(), "inputs must be a CPU tensor");
    TORCH_CHECK(weights.device().is_cpu(), "weights must be a CPU tensor");
    TORCH_CHECK(inputs.dtype() == torch::kInt16, "inputs must be int16");
    TORCH_CHECK(weights.dtype() == torch::kInt8, "weights must be int8 (1.58-bit)");
    
    // weights are expected to be [out_features, in_features]
    int batch_size = inputs.size(0);
    int in_features = inputs.size(1);
    int out_features = weights.size(0);
    
    TORCH_CHECK(weights.size(1) == in_features, "input and weight dimensions do not match");

    // Output is 32-bit integer to prevent overflow
    auto outputs = torch::empty({batch_size, out_features}, torch::dtype(torch::kInt32).device(torch::kCPU));

    const int16_t* inputs_ptr = inputs.data_ptr<int16_t>();
    const int8_t* weights_ptr = weights.data_ptr<int8_t>();
    int32_t* outputs_ptr = outputs.data_ptr<int32_t>();

    bitnet_avx2_forward(inputs_ptr, weights_ptr, outputs_ptr, batch_size, in_features, out_features);

    return outputs;
}

PYBIND11_MODULE(TORCH_EXTENSION_NAME, m) {
    m.def("bitnet_matmul", &bitnet_matmul, "AVX2 1.58-bit Matrix Multiplication (Pure Add/Sub)");
}
