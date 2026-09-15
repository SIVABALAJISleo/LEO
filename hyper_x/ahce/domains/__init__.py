"""
hyper_x/ahce/domains/__init__.py
================================
Domain adapters for AHCE (Section 18).
"""

from .ai import AIDomainAdapter
from .llm import LLMDomainAdapter
from .graphics import GraphicsDomainAdapter
from .ray import RayDomainAdapter
from .math import MathDomainAdapter
from .scientific import ScientificDomainAdapter
from .media import MediaDomainAdapter
from .rag import RAGDomainAdapter

__all__ = [
    "AIDomainAdapter",
    "LLMDomainAdapter",
    "GraphicsDomainAdapter",
    "RayDomainAdapter",
    "MathDomainAdapter",
    "ScientificDomainAdapter",
    "MediaDomainAdapter",
    "RAGDomainAdapter",
]
