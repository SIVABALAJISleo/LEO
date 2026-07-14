from setuptools import setup, Extension
from torch.utils import cpp_extension
import os

# Detect if we are on Windows
is_windows = os.name == 'nt'

# Compilation flags
extra_compile_args = []
if is_windows:
    # MSVC flags for AVX2
    extra_compile_args = ['/O2', '/arch:AVX2']
else:
    # GCC/Clang flags for AVX2
    extra_compile_args = ['-O3', '-mavx2', '-mfma']

setup(
    name='bitnet_avx2_ext',
    ext_modules=[
        cpp_extension.CppExtension(
            name='core_ai.kernels.bitnet_avx2_ext',
            sources=[
                'core_ai/kernels/bindings.cpp',
                'core_ai/kernels/bitnet_avx2.cpp'
            ],
            extra_compile_args=extra_compile_args
        )
    ],
    cmdclass={
        'build_ext': cpp_extension.BuildExtension
    }
)
