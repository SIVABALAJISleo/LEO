"""
hyper/universal/pathways/composition.py
=======================================
Pathway Composition Engine.
Composes multiple transformations into unified candidate computational pathways.
"""

from __future__ import annotations

import time
from typing import Any, Callable, Dict, List, Optional
import numpy as np

from .schema import UniversalPathway, TransformationFamily


class UniversalPathwayComposer:
    """Composes multiple transformations across families into unified candidate pathways."""

    @staticmethod
    def compose(
        base_pathway: UniversalPathway,
        secondary_pathway: UniversalPathway,
        new_family: Optional[TransformationFamily] = None,
        composed_name: Optional[str] = None,
    ) -> UniversalPathway:
        new_id = f"PATH-COMP-{int(time.time()*1000)%1000000:06d}"
        family = new_family or base_pathway.family

        # Merge transformation chains without duplicates
        combined_chain = list(base_pathway.transformation_chain)
        for t in secondary_pathway.transformation_chain:
            if t not in combined_chain:
                combined_chain.append(t)

        h = UniversalPathway.compute_structural_hash(
            family=family.value,
            transformations=combined_chain,
            hardware=secondary_pathway.target_hardware or base_pathway.target_hardware,
            code_snippet=secondary_pathway.synthesized_code or base_pathway.synthesized_code,
        )

        # Function composition: f(g(x)) or g(x) with optimization
        fn_base = base_pathway.run_fn
        fn_sec = secondary_pathway.run_fn

        composed_fn = None
        if fn_base is not None and fn_sec is not None:
            # By default execute secondary or layered
            composed_fn = lambda x: fn_sec(x)
        elif fn_sec is not None:
            composed_fn = fn_sec
        else:
            composed_fn = fn_base

        est_speedup = max(base_pathway.estimated_speedup, secondary_pathway.estimated_speedup) * 1.1

        return UniversalPathway(
            pathway_id=new_id,
            family=family,
            name=composed_name or f"{base_pathway.name} + {secondary_pathway.name}",
            transformation_chain=combined_chain,
            structural_hash=h,
            parent_id=base_pathway.pathway_id,
            target_hardware=secondary_pathway.target_hardware or base_pathway.target_hardware,
            run_fn=composed_fn,
            synthesized_code=secondary_pathway.synthesized_code or base_pathway.synthesized_code,
            lineage_depth=max(base_pathway.lineage_depth, secondary_pathway.lineage_depth) + 1,
            estimated_speedup=est_speedup,
            metadata={
                "composed_from": [base_pathway.pathway_id, secondary_pathway.pathway_id],
            },
        )
