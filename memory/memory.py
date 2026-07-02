# Hot-cache memory state with Topological Hypergraph backing
from core_ai.fabric.topological_hypergraph import TopologicalHypergraph

HOT_CACHE = {}
HYPERGRAPH = TopologicalHypergraph()

def get_state(key: str):
    # Try hypergraph reconstruction first
    holographic_sig = key.encode('utf-8')
    recon = HYPERGRAPH.reconstruct_from_interference(holographic_sig)
    if recon and recon.get("reconstructed_data"):
        return recon["reconstructed_data"]
    return HOT_CACHE.get(key, "NULL")

def set_state(key: str, value: str):
    HOT_CACHE[key] = value
    # Register fractal node in hypergraph
    HYPERGRAPH.insert_fractal_node(key, value.encode('utf-8'))

