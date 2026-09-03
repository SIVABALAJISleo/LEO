"""
hyper_v3/ir/dependency.py
Defines typed dependency edges between computation nodes.
"""

from dataclasses import dataclass
from enum import Enum


class DependencyType(Enum):
    DATA_FLOW = "DATA_FLOW"
    CONTROL_FLOW = "CONTROL_FLOW"
    MEMORY_ORDERING = "MEMORY_ORDERING"
    SYNC_BARRIER = "SYNC_BARRIER"


@dataclass
class DependencyEdge:
    source_node_id: str
    target_node_id: str
    dep_type: DependencyType = DependencyType.DATA_FLOW
    tensor_name: str = ""
