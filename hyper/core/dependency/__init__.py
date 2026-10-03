"""
hyper/core/dependency/__init__.py
Dependency graph and slice analysis.
"""
from hyper.core.dependency.analyzer import DataDependencyGraph, DependencyEdge

__all__ = ["DataDependencyGraph", "DependencyEdge"]
