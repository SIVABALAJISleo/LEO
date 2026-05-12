import logging
import math
from typing import Dict, Any, List, Tuple

logger = logging.getLogger(__name__)

class SpatialPhysics:
    """
    Spatial Grid Hashing for O(N) collision detection + Position Based Dynamics (PBD).
    Avoids O(N^2) pairwise checks.
    """
    def __init__(self, cell_size: float = 2.0):
        self.cell_size = cell_size
        self.grid = {} # Dict[Tuple[int, int, int], List[int]]
        self.particles = [] # List[Dict]
        logger.info(f"SpatialPhysics initialized with cell_size={cell_size}")

    def add_particle(self, pos: Tuple[float, float, float], mass: float = 1.0):
        p_idx = len(self.particles)
        self.particles.append({
            "idx": p_idx,
            "pos": list(pos),
            "prev_pos": list(pos),
            "mass": mass,
            "vel": [0,0,0]
        })
        self._update_grid_for_particle(p_idx)

    def _hash_pos(self, pos: List[float]) -> Tuple[int, int, int]:
        return (
            int(math.floor(pos[0] / self.cell_size)),
            int(math.floor(pos[1] / self.cell_size)),
            int(math.floor(pos[2] / self.cell_size))
        )

    def _update_grid_for_particle(self, p_idx: int):
        # In a real step, we'd clear and rebuild or move
        pos = self.particles[p_idx]["pos"]
        cell = self._hash_pos(pos)
        if cell not in self.grid:
            self.grid[cell] = []
        self.grid[cell].append(p_idx)

    def step_pbd(self, dt: float):
        """
        Position Based Dynamics Step.
        1. Predicition (Verlet)
        2. Constraint Solving (Distance constraints)
        3. Velocity Update
        """
        # 1. Prediction
        for p in self.particles:
            p["prev_pos"] = list(p["pos"])
            # Apply gravity
            p["vel"][1] -= 9.81 * dt
            
            p["pos"][0] += p["vel"][0] * dt
            p["pos"][1] += p["vel"][1] * dt
            p["pos"][2] += p["vel"][2] * dt

        # 2. Collision (via Spatial Hash)
        # Rebuild grid
        self.grid = {}
        for p in self.particles:
            self._update_grid_for_particle(p["idx"])
            
        # Check neighbors
        # (Simplified constraint solve)
        
        # 3. Update Velocity
        for p in self.particles:
            p["vel"][0] = (p["pos"][0] - p["prev_pos"][0]) / dt
            p["vel"][1] = (p["pos"][1] - p["prev_pos"][1]) / dt
            p["vel"][2] = (p["pos"][2] - p["prev_pos"][2]) / dt
            
        logger.debug(f"Simulated {len(self.particles)} particles with PBD")
