"""
hyper_v3/learning/workload_model.py
Predicts operational memory footprint and complexity from input tensor shapes.
"""

from typing import Dict, Any, List
import numpy as np


class WorkloadModel:
    @staticmethod
    def extract_features(workload_name: str, input_shapes: List[List[int]]) -> Dict[str, Any]:
        total_elements = sum(int(np.prod(s)) for s in input_shapes)
        return {
            "workload": workload_name,
            "total_elements": total_elements,
            "estimated_memory_mb": (total_elements * 4) / (1024 * 1024)
        }
