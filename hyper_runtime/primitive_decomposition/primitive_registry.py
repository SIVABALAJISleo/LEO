from typing import List, Dict

class CognitivePrimitive:
    def __init__(self, name: str, layer: int, description: str):
        self.name = name
        self.layer = layer # 0: Mathematical, 1: Domain Stable, 2: Business Composition
        self.description = description

class PrimitiveRegistry:
    """
    Registers the formal stable cognitive primitives for LEO.
    """
    def __init__(self):
        self.primitives: Dict[str, CognitivePrimitive] = {}
        self._load_default_primitives()
        
    def register(self, name: str, layer: int, description: str):
        self.primitives[name.lower()] = CognitivePrimitive(name, layer, description)
        
    def _load_default_primitives(self):
        # Layer 0: Mathematical Substrate
        math_prims = ["transform", "filter", "aggregate", "compare", "sequence", "branch", "recursion", "optimize", "search"]
        for p in math_prims:
            self.register(p, 0, f"Mathematical base operator: {p}")
            
        # Layer 1: Domain Stable Primitives
        domain_prims = ["extract", "classify", "summarize", "validate", "compare", "route", "flag", "escalate", "negotiate", "simulate", "evaluate", "infer", "plan"]
        for p in domain_prims:
            self.register(p, 1, f"Domain stable cognitive operator: {p}")
            
        # Layer 2: Business Compositions
        business_prims = ["invoice_review", "contract_analysis", "risk_assessment", "compliance_verification", "workflow_escalation", "policy_enforcement"]
        for p in business_prims:
            self.register(p, 2, f"End-to-end enterprise workflow: {p}")
            
    def get_primitive(self, name: str) -> CognitivePrimitive:
        return self.primitives.get(name.lower())
        
    def list_primitives(self) -> List[str]:
        return list(self.primitives.keys())
