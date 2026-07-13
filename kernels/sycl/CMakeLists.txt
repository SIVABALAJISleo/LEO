cmake_minimum_required(VERSION 3.20)
project(leo_sycl_kernels CXX)

# Find Intel oneAPI SYCL compiler (DPC++)
set(CMAKE_CXX_COMPILER "icx")

# Find PyBind11
find_package(Python3 COMPONENTS Interpreter Development REQUIRED)
find_package(pybind11 CONFIG REQUIRED)

# Add SYCL flags for Intel compilation
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fsycl -fsycl-targets=spir64_gen -O3")

# Create Python Module
pybind11_add_module(leo_sycl_kernels leo_custom_sycl.cpp)

# Link against SYCL runtime
target_link_libraries(leo_sycl_kernels PRIVATE sycl)
