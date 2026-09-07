"""
cbe/validation/__init__.py
Validation subsystem for numerical correctness, visual quality contracts,
regression detection, and adversarial stress testing.
"""

from .correctness import CorrectnessValidator
from .visual_quality import VisualQualityValidator
from .regression import RegressionAuditor, BaselineThresholds
from .adversarial import AdversarialStressTester, AdversarialTestReport

__all__ = [
    "CorrectnessValidator",
    "VisualQualityValidator",
    "RegressionAuditor",
    "BaselineThresholds",
    "AdversarialStressTester",
    "AdversarialTestReport",
]
