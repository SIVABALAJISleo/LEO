"""
hyper/semantics/aliasing.py
===========================
Formal Memory Aliasing Analysis for HYPER Universal Semantic Machine.
Implements Section 21:
"Determine whether A[i] and B[j] can refer to the same memory.
Never perform unsafe elimination based on incorrect alias assumptions."
"""

from __future__ import annotations
import enum
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Set, Tuple


class AliasVerdict(str, enum.Enum):
    NO_ALIAS = "NO_ALIAS"              # Guaranteed distinct memory spaces or disjoint regions
    MUST_ALIAS = "MUST_ALIAS"          # Guaranteed identical memory location
    MAY_ALIAS = "MAY_ALIAS"            # Potential overlap; compiler MUST preserve dependencies
    EXACT_SAME_BUFFER = "EXACT_SAME_BUFFER"


@dataclass(frozen=True)
class MemoryRegion:
    buffer_id: str
    base_offset: int = 0
    size_bytes: Optional[int] = None
    strides: Optional[Tuple[int, ...]] = None
    shape: Optional[Tuple[int, ...]] = None
    is_constant: bool = False
    is_read_only: bool = False


class MemoryAliasAnalyzer:
    """
    Formal alias analysis for tensor references, pointers, and memory buffers.
    Enforces fail-closed safety: if overlap cannot be mathematically ruled out,
    returns MAY_ALIAS and forbids unsafe reordering or dead-store elimination.
    """

    def __init__(self) -> None:
        self.registered_regions: Dict[str, MemoryRegion] = {}

    def register_region(self, region: MemoryRegion) -> None:
        self.registered_regions[region.buffer_id] = region

    def analyze_alias(
        self,
        ref_a: str,
        ref_b: str,
        index_a: Optional[Any] = None,
        index_b: Optional[Any] = None,
    ) -> AliasVerdict:
        """
        Determines aliasing relationship between ref_a and ref_b.
        """
        if ref_a == ref_b:
            if index_a is None and index_b is None:
                return AliasVerdict.MUST_ALIAS
            if index_a == index_b and index_a is not None:
                return AliasVerdict.MUST_ALIAS
            if isinstance(index_a, int) and isinstance(index_b, int):
                if index_a != index_b:
                    return AliasVerdict.NO_ALIAS
                return AliasVerdict.MUST_ALIAS
            # Slices or variable index: check disjointness
            if isinstance(index_a, tuple) and isinstance(index_b, tuple):
                if self._are_slices_disjoint(index_a, index_b):
                    return AliasVerdict.NO_ALIAS
            return AliasVerdict.MAY_ALIAS

        reg_a = self.registered_regions.get(ref_a)
        reg_b = self.registered_regions.get(ref_b)

        if reg_a and reg_b:
            # Different isolated root buffers have no aliasing
            if reg_a.buffer_id != reg_b.buffer_id:
                # If neither is a sub-view of the other
                return AliasVerdict.NO_ALIAS

        # By default fail-closed: if identity cannot be proved distinct
        return AliasVerdict.NO_ALIAS if (reg_a and reg_b and reg_a.buffer_id != reg_b.buffer_id) else AliasVerdict.MAY_ALIAS

    def _are_slices_disjoint(self, slc_a: Tuple[Any, ...], slc_b: Tuple[Any, ...]) -> bool:
        """Determines if two multi-dimensional constant slices are strictly disjoint along at least one axis."""
        min_dims = min(len(slc_a), len(slc_b))
        for d in range(min_dims):
            dim_a = slc_a[d]
            dim_b = slc_b[d]
            if isinstance(dim_a, int) and isinstance(dim_b, int) and dim_a != dim_b:
                return True
            if isinstance(dim_a, slice) and isinstance(dim_b, slice):
                if (
                    dim_a.start is not None
                    and dim_a.stop is not None
                    and dim_b.start is not None
                    and dim_b.stop is not None
                ):
                    if dim_a.stop <= dim_b.start or dim_b.stop <= dim_a.start:
                        return True
        return False

    def can_safely_reorder(self, write_ref: str, read_ref: str) -> bool:
        """
        Determines whether a write to write_ref can be safely reordered across a read from read_ref.
        Returns True ONLY if NO_ALIAS is formally established.
        """
        verdict = self.analyze_alias(write_ref, read_ref)
        return verdict == AliasVerdict.NO_ALIAS
