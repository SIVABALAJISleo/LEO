"""
hyper/escape_engine/workloads/__init__.py
========================================
VAEE Initial Research Workloads Suite.
"""

from .matrix_multiplication import MatrixMultiplicationResearchWorkload
from .polynomial import PolynomialResearchWorkload
from .sorting import SortingResearchWorkload
from .convolution_2d import Convolution2DResearchWorkload
from .dynamic_programming import DynamicProgrammingResearchWorkload

__all__ = [
    "MatrixMultiplicationResearchWorkload",
    "PolynomialResearchWorkload",
    "SortingResearchWorkload",
    "Convolution2DResearchWorkload",
    "DynamicProgrammingResearchWorkload",
]
