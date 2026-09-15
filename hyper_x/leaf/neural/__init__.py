"""
hyper_x/leaf/neural/__init__.py
===============================
Neural Implicit Resolution (NIR) Package for LEAF.
"""

from .implicit_field import NeuralImplicitField, SinusoidalActivation
from .trainer import NIRTrainer, NIRCostReport
from .distillation import NeuralDistiller
from .surrogate import NeuralSurrogate
from .verifier import NIRGeneralizationVerifier, NIRGeneralizationAudit

__all__ = [
    "NeuralImplicitField",
    "SinusoidalActivation",
    "NIRTrainer",
    "NIRCostReport",
    "NeuralDistiller",
    "NeuralSurrogate",
    "NIRGeneralizationVerifier",
    "NIRGeneralizationAudit",
]
