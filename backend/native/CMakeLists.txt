cmake_minimum_required(VERSION 3.15)
project(HyperCompute LANGUAGES CXX C)

# COMPILER OPTIMIZATION
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Enable maximum performance flags
set(CMAKE_CXX_FLAGS "-O3 -march=native -ffast-math -funroll-loops -fno-strict-aliasing ${CMAKE_CXX_FLAGS}")
set(CMAKE_C_FLAGS "-O3 -march=native -ffast-math -funroll-loops -fno-strict-aliasing ${CMAKE_C_FLAGS}")

# 1. ISPC explicit SIMD
find_program(ISPC_EXECUTABLE ispc)
if(NOT ISPC_EXECUTABLE)
    message(WARNING "ISPC not found, SIMD optimizations might degrade to auto-vectorization.")
else()
    set(ISPC_FLAGS "--target=avx2-i32x8,avx512skx-i32x16,neon-i32x4" "--opt=fast-math" "-O3")
endif()

# 2. LINEAR ALGEBRA ACCELERATION (libxsmm / OpenBLAS)
find_package(BLAS)
if(BLAS_FOUND)
    message(STATUS "Found BLAS: ${BLAS_LIBRARIES}")
endif()

# 5. iGPU ACCELERATION (Vulkan fallback)
find_package(Vulkan)
if(Vulkan_FOUND)
    message(STATUS "Found Vulkan: ${Vulkan_LIBRARIES}")
    add_definitions(-DENABLE_VULKAN_COMPUTE)
endif()

# Optional: TVM / OpenVINO / oneDNN linkage can be added here if building custom operators.

# Define library and export
add_library(hyper_native SHARED 
    simd_wrapper.cpp
)

if(ISPC_EXECUTABLE)
    add_custom_command(
        OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/math_kernels.o
        COMMAND ${ISPC_EXECUTABLE} ${ISPC_FLAGS} -o ${CMAKE_CURRENT_BINARY_DIR}/math_kernels.o ${CMAKE_CURRENT_SOURCE_DIR}/math_kernels.ispc
        DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/math_kernels.ispc
    )
    target_link_libraries(hyper_native PRIVATE ${CMAKE_CURRENT_BINARY_DIR}/math_kernels.o)
endif()

if(BLAS_FOUND)
    target_link_libraries(hyper_native PRIVATE ${BLAS_LIBRARIES})
endif()

if(Vulkan_FOUND)
    target_link_libraries(hyper_native PRIVATE Vulkan::Vulkan)
endif()
