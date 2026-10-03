"""
hyper/core/adapters/__init__.py
Application adapters for llama.cpp, ONNX Runtime, OpenVINO, RAG, etc.
"""
from hyper.core.adapters.domain_adapters import DomainAdapter, DomainAdapterRegistry

__all__ = ["DomainAdapter", "DomainAdapterRegistry"]
