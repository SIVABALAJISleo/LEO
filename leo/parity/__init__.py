"""
leo/parity/__init__.py
======================
Contract-Driven, Falsifiable Parity Engine for LEO / HYPER.

Hardware: Intel Core i5-12450H + Intel UHD iGPU + 16GB RAM + Windows 11.
Restrictions: Software-only, no discrete GPU silicon, no remote cloud, no paid compute.
"""

from .contracts import (
    ContractDef,
    ContractsRegistry,
    ExecutionResult,
    ResultLabel,
    load_and_freeze_contracts,
)
from .runner import ParityBenchmarkRunner, ParityCertificate
from .router import ParityWorkloadRouter

__all__ = [
    "ContractDef",
    "ContractsRegistry",
    "ExecutionResult",
    "ResultLabel",
    "load_and_freeze_contracts",
    "ParityBenchmarkRunner",
    "ParityCertificate",
    "ParityWorkloadRouter",
]
