@echo off
echo Building Max-Efficiency Intel Core (AVX2/Zero-Compute)...
echo Hardware Target: Intel CPU (AVX2 instructions) + shared iGPU memory layout.

:: Try to compile using g++ (MinGW/MSYS2) which is common for llama.cpp local builds
g++ -O3 -mavx2 -shared -fPIC -o native_engine\bin\intel_zero_compute_core.dll native_engine\src\intel_zero_compute_core.cpp

if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] G++ failed. Trying MSVC...
    :: Fallback to MSVC if g++ is not available
    cl.exe /O2 /arch:AVX2 /LD /Fe:native_engine\bin\intel_zero_compute_core.dll native_engine\src\intel_zero_compute_core.cpp
)

echo.
echo Build complete. The DLL is ready for Python orchestration zero-overhead binding.
