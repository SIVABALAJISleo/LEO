# Static knowledge maps with Topological Hypergraph backing
from core_ai.fabric.topological_hypergraph import TopologicalHypergraph

DOMAIN_MAP = {
    "NVIDIA": "TECH_ENTITY",
    "HYPER": "CORE_SYSTEM"
}

HYPERGRAPH = TopologicalHypergraph()

def resolve_entity(name: str):
    # Try hypergraph lookup/traversal
    hops = HYPERGRAPH.traverse_topological(name, depth=2)
    if hops and len(hops) > 1:
        return f"RESOLVED_VIA_HYPERGRAPH_{'_'.join(hops)}"
    return DOMAIN_MAP.get(name, "UNKNOWN")

