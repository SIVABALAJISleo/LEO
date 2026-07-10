from setuptools import setup, find_packages

setup(
    name="leo_infinity_kernels",
    version="2.0.0",
    author="LEO AI / SIVABALAJISleo",
    author_email="leo@example.com",
    description="High-performance CPU/iGPU execution kernels — NVIDIA-irrelevant inference on consumer hardware",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/SIVABALAJISleo/LEO",
    packages=find_packages(),
    license="MIT",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=["numpy>=1.21"],
    extras_require={
        "benchmark": ["psutil"],
        "huggingface": ["transformers", "torch"],
    },
    entry_points={
        "console_scripts": [
            "leo-bench-kernels=leo_infinity_kernels.benchmarks.bench_kernels:main",
        ],
    },
)
