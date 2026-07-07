import re
import logging
from typing import Dict, Any
from .primitive_registry import PrimitiveRegistry

logger = logging.getLogger("HyperCore.DecompositionEngine")

class PrimitiveDecompositionEngine:
    """
    HyperCore PHASE 1 — Primitive Decomposition Engine
    
    Translates loose natural-language queries into a structured graph of
    reusable mathematical (Layer 0) and cognitive (Layer 1) primitives,
    completely preventing unconstrained open-ended model generation.
    """
    def __init__(self):
        self.registry = PrimitiveRegistry()
        
        # Mapping keyword signals to primitives to simulate semantic extraction
        self.rules = [
            (r"\b(review|analyze|audit)\b.*\b(contract|agreement|legal)\b", ["contract_analysis", "extract", "compare"]),
            (r"\b(verify|check|enforce|comply)\b.*\b(policy|regulation|compliance)\b", ["compliance_verification", "validate", "flag"]),
            (r"\b(summarize|tldr|compress)\b", ["summarize"]),
            (r"\b(reconcile|match|calculate|diff)\b.*\b(invoice|ledger|financial)\b", ["invoice_review", "compare", "aggregate"]),
            (r"\b(escalate|alert|warn)\b", ["escalate", "flag"])
        ]
        
    def decompose(self, query: str) -> Dict[str, Any]:
        """
        Decomposes an enterprise query into dynamic cognitive pipelines.
        Tracks ambiguity rate and marks primitive coverage gaps.
        """
        query_clean = query.lower()
        matched_primitives = []
        
        # 1. Pipeline extraction based on semantic rules
        for pattern, prims in self.rules:
            if re.search(pattern, query_clean):
                matched_primitives.extend(prims)
                
        # Remove duplicates preserving order
        unique_prims = []
        for p in matched_primitives:
            if p not in unique_prims:
                unique_prims.append(p)
                
        # 2. Ambiguity & Gaps Calculation
        # High ambiguity is reported if multiple unrelated pipelines match,
        # or if zero primitives match (semantic gap)
        ambiguity_rate = 0.0
        primitive_gap = False
        
        if len(unique_prims) == 0:
            primitive_gap = True
            ambiguity_rate = 1.0 # 100% Ambiguous if we have no prior primitives
        elif len(unique_prims) > 3:
            # Overlapping rules cause high structural ambiguity
            ambiguity_rate = 0.65
            
        # 3. Dynamic execution DAG construction
        pipeline_dag = []
        for idx, prim in enumerate(unique_prims):
            meta = self.registry.get_primitive(prim)
            if meta:
                pipeline_dag.append({
                    "step": idx + 1,
                    "primitive": prim,
                    "layer": meta.layer,
                    "description": meta.description
                })
                
        return {
            "query": query,
            "pipeline": pipeline_dag,
            "ambiguity_rate": ambiguity_rate,
            "primitive_gap": primitive_gap,
            "coverage_score": 1.0 - (1.0 if primitive_gap else ambiguity_rate)
        }
