"""
hyper/frontends/frontend_registry.py
====================================
Frontend Registry for LEO / HYPER Universal Exact Semantic Machine.
Implements Sections 23, 24, 25, 26:
- Registry of frontends declaring supported constructs and semantic guarantees
- Fail-closed error reporting for unsupported operations
"""

from __future__ import annotations
import abc
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Type
from hyper.universal_ir.program import UniversalIRProgram


class UnsupportedSemanticError(RuntimeError):
    """
    Explicit exception raised when a workload contains constructs outside
    the formally supported semantic domain of the candidate frontend.
    Never silently approximated.
    """
    def __init__(self, semantic_code: str, details: str) -> None:
        self.semantic_code = semantic_code
        self.details = details
        super().__init__(f"UNSUPPORTED_SEMANTIC [{semantic_code}]: {details}")


@dataclass(frozen=True)
class FrontendMetadata:
    name: str
    version: str
    supported_constructs: List[str]
    semantic_guarantees: str
    description: str


class BaseFrontend(abc.ABC):
    """Abstract base class for all HYPER language / graph frontends."""

    @classmethod
    @abc.abstractmethod
    def metadata(cls) -> FrontendMetadata:
        pass

    @abc.abstractmethod
    def import_to_ir(self, source: Any) -> UniversalIRProgram:
        """Parses and converts source workload into authoritative UniversalIRProgram."""
        pass


class FrontendRegistry:
    """Central registry of all verified workload frontends."""

    _frontends: Dict[str, Type[BaseFrontend]] = {}

    @classmethod
    def register(cls, frontend_cls: Type[BaseFrontend]) -> None:
        meta = frontend_cls.metadata()
        cls._frontends[meta.name.lower()] = frontend_cls

    @classmethod
    def get(cls, name: str) -> Optional[Type[BaseFrontend]]:
        return cls._frontends.get(name.lower())

    @classmethod
    def list_frontends(cls) -> List[FrontendMetadata]:
        return [f_cls.metadata() for f_cls in cls._frontends.values()]
