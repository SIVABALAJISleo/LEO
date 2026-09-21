"""
hyper/universal/pathways/mathematical.py
========================================
Family 1: Mathematical Transformations.
- Horner's rule polynomial evaluation: O(N) vs O(N^2)
- Common subexpression elimination (CSE)
- Algebraic identities and factorization
- Strassen / low-rank bilinear forms
"""

from __future__ import annotations

import time
from typing import Any, Callable, Dict, List, Optional
import numpy as np

from .schema import UniversalPathway, TransformationFamily


class MathematicalTransformations:
    """Generates mathematical formulation escapes."""

    @staticmethod
    def create_horner_pathway(degree: int, coeffs: Optional[np.ndarray] = None) -> UniversalPathway:
        """Horner's rule converts O(N^2) direct polynomial powers to O(N) nested multiply-adds."""
        pid = f"PATH-MATH-HORNER-{int(time.time()*1000)%1000000:06d}"
        chain = ["ALGEBRAIC_FACTORIZATION", "HORNERS_NESTED_RULE", "COMMON_SUBEXPRESSION_ELIMINATION"]

        def horner_eval(x: Any, c_arr: Optional[np.ndarray] = coeffs) -> Any:
            if c_arr is None:
                return x
            if isinstance(x, np.ndarray):
                res = np.full_like(x, c_arr[-1])
                for c in c_arr[-2::-1]:
                    res = res * x + c
                return res
            # Scalar
            res = c_arr[-1]
            for c in c_arr[-2::-1]:
                res = res * x + c
            return float(res)

        h = UniversalPathway.compute_structural_hash(
            family=TransformationFamily.MATHEMATICAL.value,
            transformations=chain,
            hardware="CPU_AVX2",
        )

        return UniversalPathway(
            pathway_id=pid,
            family=TransformationFamily.MATHEMATICAL,
            name="Horner's Rule Polynomial Reformulation",
            transformation_chain=chain,
            structural_hash=h,
            target_hardware="CPU_AVX2",
            run_fn=horner_eval,
            estimated_speedup=10.0,
            metadata={"degree": degree, "complexity": "O(N)"},
        )

    @staticmethod
    def create_cse_pathway(name: str = "algebraic_cse") -> UniversalPathway:
        pid = f"PATH-MATH-CSE-{int(time.time()*1000)%1000000:06d}"
        chain = ["COMMON_SUBEXPRESSION_ELIMINATION", "EXPRESSION_HOISTING"]
        h = UniversalPathway.compute_structural_hash(
            family=TransformationFamily.MATHEMATICAL.value,
            transformations=chain,
            hardware="CPU_AVX2",
        )
        return UniversalPathway(
            pathway_id=pid,
            family=TransformationFamily.MATHEMATICAL,
            name=f"CSE Elimination: {name}",
            transformation_chain=chain,
            structural_hash=h,
            target_hardware="CPU_AVX2",
            estimated_speedup=1.3,
        )
