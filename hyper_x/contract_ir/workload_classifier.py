#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
hyper_x/contract_ir/workload_classifier.py
==========================================
Classifies raw workloads into formal domain families.
"""

from typing import Any, Dict
import numpy as np


def classify_workload(workload_name: str, input_data: Any) -> str:
    """
    Classifies workload into one of:
      - DENSE_LINEAR_ALGEBRA
      - SPARSE_LINEAR_ALGEBRA
      - LLM_INFERENCE
      - EMBEDDING_SEARCH
      - GRAPHICS_TEMPORAL
      - SCIENTIFIC_SIMULATION
      - GENERIC_COMPUTE
    """
    name_lower = workload_name.lower()

    if any(k in name_lower for k in ["gemm", "matmul", "linear", "dense", "blas", "projection"]):
        return "DENSE_LINEAR_ALGEBRA"
    elif any(k in name_lower for k in ["sparse", "csr", "coo", "spmm"]):
        return "SPARSE_LINEAR_ALGEBRA"
    elif any(k in name_lower for k in ["llm", "language", "token", "prompt", "transformer", "attention"]):
        return "LLM_INFERENCE"
    elif any(k in name_lower for k in ["embed", "rag", "retrieval", "faiss", "vector"]):
        return "EMBEDDING_SEARCH"
    elif any(k in name_lower for k in ["render", "graphics", "shader", "frame", "ray", "pixel", "video"]):
        return "GRAPHICS_TEMPORAL"
    elif any(k in name_lower for k in ["simulation", "pde", "cfd", "physics", "finite_element", "fft"]):
        return "SCIENTIFIC_SIMULATION"
    else:
        # Fallback inspection by data type/shape
        if isinstance(input_data, np.ndarray):
            return "DENSE_LINEAR_ALGEBRA" if input_data.ndim >= 2 else "GENERIC_COMPUTE"
        elif isinstance(input_data, str):
            return "LLM_INFERENCE"
        return "GENERIC_COMPUTE"
