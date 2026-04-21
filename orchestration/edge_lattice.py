import hashlib
import json
import logging
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

class EdgeLattice:
    """
    Module 42: CLIENT-SIDE SYMBOLIC LATTICE (SEI Edge)
    Enforces 'Correctness-by-Construction' on the client.
    Maps symbol sequences into deterministic 64-bit Query IDs.
    """
    def __init__(self):
        # The symbol graph (Trie-based lattice)
        # Root -> Action -> Entity -> Parameter
        self.lattice = {
            "GET": {
                "STATUS": ["ALPHA", "BETA", "GAMMA"],
                "METRICS": ["CPU", "MEM", "IO"]
            },
            "SET": {
                "POWER": ["ON", "OFF", "REBOOT"]
            }
        }
        
    def get_valid_next(self, current_path: List[str]) -> List[str]:
        """Returns valid next symbols based on current traversal."""
        node = self.lattice
        for symbol in current_path:
            if isinstance(node, dict) and symbol in node:
                node = node[symbol]
            else:
                return []
        
        if isinstance(node, dict):
            return list(node.keys())
        if isinstance(node, list):
            return node
        return []

    def finalize_query(self, path: List[str]) -> int:
        """
        Collapses a symbol path into a deterministic 64-bit ID.
        This is the only thing sent to the backend in the Fast Path.
        """
        path_str = "->".join(path).upper()
        # Use a stable hash to generate the ID
        h = hashlib.sha256(path_str.encode()).hexdigest()
        # Take first 16 chars for 64-bit integer
        return int(h[:16], 16) % 1048576

class SEILinker:
    """
    Links the Edge Lattice to the Native SEI Engine.
    """
    def __init__(self):
        self.lattice = EdgeLattice()
        
    def simulate_ui_interaction(self, input_sequence: List[str]) -> Dict[str, Any]:
        print(f"--- Edge Lattice UI Simulator ---")
        path = []
        for symbol in input_sequence:
            valid_options = self.lattice.get_valid_next(path)
            if symbol in valid_options:
                path.append(symbol)
                print(f"Selection: {symbol} | Valid Next: {self.lattice.get_valid_next(path)}")
            else:
                print(f"Invalid State Avoided: {symbol} is not valid after {'->'.join(path)}")
                break
        
        query_id = self.lattice.finalize_query(path)
        print(f"Generated QUERY_ID: {query_id} (Path: {'->'.join(path)})")
        
        return {
            "query_id": query_id,
            "intent_raw": "->".join(path),
            "status": "DETERMINISTIC_SEI"
        }

if __name__ == "__main__":
    linker = SEILinker()
    
    # Valid Path
    print("\nCase 1: Construction of a valid query")
    linker.simulate_ui_interaction(["GET", "STATUS", "ALPHA"])
    
    # Invalid Path (Safe)
    print("\nCase 2: Attempted invalid construction")
    linker.simulate_ui_interaction(["SET", "STATUS"]) # STATUS is not in SET
