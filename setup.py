from setuptools import setup, find_packages

setup(
    name="hyper-sdk",
    version="1.0.0",
    description="Official Python Developer SDK for Project HYPER Enterprise AI Platform",
    author="Project HYPER SRE",
    packages=find_packages(),
    install_requires=[
        "httpx>=0.27.0",
        "tenacity>=8.3.0"
    ],
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.11",
    ]
)
