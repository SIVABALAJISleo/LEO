"""
hyper/universal/adapter/workload_types.py
=========================================
Domain taxonomy, operation classifications, and data schemas for Universal Workload Intake.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional
import dataclasses


class WorkloadDomain(str, Enum):
    NUMERICAL = "NUMERICAL"
    MATRIX_TENSOR = "MATRIX_TENSOR"
    SCIENTIFIC_SIMULATION = "SCIENTIFIC_SIMULATION"
    PHYSICS_PARTICLE = "PHYSICS_PARTICLE"
    GRAPHICS_RENDERING = "GRAPHICS_RENDERING"
    IMAGE_VIDEO_PROCESSING = "IMAGE_VIDEO_PROCESSING"
    SIGNAL_PROCESSING = "SIGNAL_PROCESSING"
    CRYPTOGRAPHIC = "CRYPTOGRAPHIC"
    COMPRESSION_DECOMPRESSION = "COMPRESSION_DECOMPRESSION"
    SEARCH_SORTING = "SEARCH_SORTING"
    GRAPH_NETWORK = "GRAPH_NETWORK"
    OPTIMIZATION_SOLVER = "OPTIMIZATION_SOLVER"
    DATABASE_ANALYTICS = "DATABASE_ANALYTICS"
    MACHINE_LEARNING_INFERENCE = "MACHINE_LEARNING_INFERENCE"
    MACHINE_LEARNING_TRAINING = "MACHINE_LEARNING_TRAINING"
    COMPUTER_VISION = "COMPUTER_VISION"
    THREE_DIMENSIONAL = "THREE_DIMENSIONAL"
    DYNAMIC_PROGRAMMING = "DYNAMIC_PROGRAMMING"
    CUSTOM_USER_CODE = "CUSTOM_USER_CODE"
    UNKNOWN_UNSEEN = "UNKNOWN_UNSEEN"


class WorkloadNecessityClass(str, Enum):
    REQUIRED = "REQUIRED"
    CONDITIONAL = "CONDITIONAL"
    REDUNDANT = "REDUNDANT"
    REUSABLE = "REUSABLE"
    INCREMENTAL = "INCREMENTAL"
    PREDICTABLE = "PREDICTABLE"
    RECONSTRUCTABLE = "RECONSTRUCTABLE"
    ELIMINABLE = "ELIMINABLE"
    UNKNOWN = "UNKNOWN"


@dataclasses.dataclass
class InputOutputSchema:
    input_type: str                   # "ndarray", "scalar", "sequence", "graph", "dict", "custom"
    input_shape: Optional[tuple] = None
    input_dtype: Optional[str] = None
    output_type: str = "ndarray"
    output_shape: Optional[tuple] = None
    output_dtype: Optional[str] = None
    element_count: int = 0
    estimated_bytes: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "input_type": self.input_type,
            "input_shape": list(self.input_shape) if self.input_shape else None,
            "input_dtype": self.input_dtype,
            "output_type": self.output_type,
            "output_shape": list(self.output_shape) if self.output_shape else None,
            "output_dtype": self.output_dtype,
            "element_count": self.element_count,
            "estimated_bytes": self.estimated_bytes,
        }
