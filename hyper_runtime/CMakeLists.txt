cmake_minimum_required(VERSION 3.15)
project(LeoHyperRuntime CXX)

# Find SYCL / Intel OneAPI Data Parallel C++ compiler
find_package(IntelDPCPP REQUIRED)

set(CMAKE_CXX_STANDARD 17)

# Create shared library for the SYCL Data Fetcher
add_library(sycl_fetcher SHARED sycl_data_fetcher.cpp)

# Link against SYCL
target_link_libraries(sycl_fetcher PRIVATE IntelDPCPP::SYCL)

# Output library to the current source directory so Python can easily find it
set_target_properties(sycl_fetcher PROPERTIES
    LIBRARY_OUTPUT_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
    RUNTIME_OUTPUT_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
)
