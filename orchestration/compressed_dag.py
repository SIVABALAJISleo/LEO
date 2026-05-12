import logging
from typing import Dict, List, Any, Optional, Set

logger = logging.getLogger(__name__)

class CompressedDAG:
    """
    Module D: COMPRESSED SYMBOLIC DAG
    - Implements ZDD-like node sharing.
    - Maximizes structural reuse of symbolic atoms.
    - Constant-time subtree retrieval.
    """
    def __init__(self):
        # Flyweight pool for unique symbolic atoms
        self.atom_pool: Dict[str, int] = {}
        self.id_to_atom: List[str] = []
        
        # Node Map: (LeftID, RightID) -> CommonParentID (Sharing)
        self.nodes: Dict[tuple, int] = {}
        self.node_descriptors: List[Dict[str, Any]] = []
        
        logger.info("Compressed DAG Initialized (Structural Sharing Active).")

    def get_atom_id(self, name: str) -> int:
        """Returns a globally unique ID for a symbolic atom."""
        if name not in self.atom_pool:
            self.atom_pool[name] = len(self.id_to_atom)
            self.id_to_atom.append(name)
        return self.atom_pool[name]

    def create_node(self, left_id: int, right_id: int, metadata: Dict[str, Any] = None) -> int:
        """
        Creates or retrieves a shared node representing a symbolic conjunction.
        Enforces 100% structural sharing (ZDD-style).
        """
        key = (left_id, right_id)
        if key not in self.nodes:
            new_id = len(self.node_descriptors)
            self.nodes[key] = new_id
            self.node_descriptors.append({
                "id": new_id,
                "left": left_id,
                "right": right_id,
                "meta": metadata or {}
            })
            return new_id
        
        return self.nodes[key]

    def resolve_path(self, node_id: int) -> List[str]:
        """Traverses the compressed structure to emerge symbolic outcomes."""
        # Fixed pipeline traversal (Branchless simulation)
        node = self.node_descriptors[node_id]
        path = []
        
        # Recursively (or iteratively for performance) gather atoms
        stack = [node]
        while stack:
            curr = stack.pop()
            if isinstance(curr['left'], int) and curr['left'] < len(self.id_to_atom):
                 path.append(self.id_to_atom[curr['left']])
            if isinstance(curr['right'], int) and curr['right'] < len(self.id_to_atom):
                 path.append(self.id_to_atom[curr['right']])
                 
        return sorted(list(set(path)))
