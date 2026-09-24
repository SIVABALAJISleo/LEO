"""
hyper_omega/hardware_bridge/__init__.py
=======================================
Software-Defined Virtual Silicon (SDVS) and Micro-Hardware Orchestration Engine.
Bypasses physical GPU hardware barriers via on-die dormant silicon unlocking
and algorithmic complexity collapse.
"""

from .silicon_virtualizer import (
    DormantSiliconHarvester,
    MicroHardwareCatalog,
    SoftwareDefinedVirtualSilicon,
    HardwareIrrelevanceReport,
    MicroHardwareOption,
)

__all__ = [
    "DormantSiliconHarvester",
    "MicroHardwareCatalog",
    "SoftwareDefinedVirtualSilicon",
    "HardwareIrrelevanceReport",
    "MicroHardwareOption",
]
