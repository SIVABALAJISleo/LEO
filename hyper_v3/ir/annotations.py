"""
hyper_v3/ir/annotations.py
Rich annotations attached to IR nodes for intelligence passes.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from hyper_v3.ir.operation import NecessityStatus


@dataclass
class NodeAnnotations:
    necessity: NecessityStatus = NecessityStatus.UNKNOWN
    is_fused: bool = False
    fused_into_id: Optional[str] = None
    is_dead: bool = False
    is_reused: bool = False
    reuse_source_hash: Optional[str] = None
    fingerprint: Optional[str] = None
    entropy: Optional[float] = None
    sparsity_ratio: Optional[float] = None
    variance: Optional[float] = None
    temporal_delta: Optional[float] = None
    custom_metadata: Dict[str, Any] = field(default_factory=dict)
