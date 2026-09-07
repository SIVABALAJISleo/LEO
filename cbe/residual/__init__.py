"""
cbe/residual: Residual-first computation architecture.
Detects, classifies, schedules, and renders sparse residuals
to eliminate redundant dense rendering.
"""

from .residual_detector import ResidualDetector, ResidualMetrics
from .residual_classifier import ResidualClassifier, ResidualClass, TileClassification
from .residual_scheduler import ResidualScheduler, SparseWorkSchedule
from .residual_renderer import ResidualRenderer

__all__ = [
    "ResidualDetector",
    "ResidualMetrics",
    "ResidualClassifier",
    "ResidualClass",
    "TileClassification",
    "ResidualScheduler",
    "SparseWorkSchedule",
    "ResidualRenderer",
]
