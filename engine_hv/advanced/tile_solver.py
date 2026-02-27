import numpy as np
import logging
from typing import Callable, Tuple

logger = logging.getLogger(__name__)

class TileSolver:
    """
    Splits large numerical fields into tiles to optimize cache locality and memory usage.
    Processes tiles sequentially, ideal for CPU-native 3D/Video fields.
    """
    def __init__(self, tile_size: Tuple[int, int] = (64, 64)):
        self.tile_size = tile_size

    def solve_grid(self, grid: np.ndarray, compute_func: Callable[[np.ndarray], np.ndarray]) -> np.ndarray:
        """
        Iterates over tiles and applies compute_func.
        """
        h, w = grid.shape[:2]
        output = np.zeros_like(grid)
        
        th, tw = self.tile_size
        logger.info(f"Processing grid {w}x{h} in tiles of {tw}x{th}")
        
        for y in range(0, h, th):
            for x in range(0, w, tw):
                # Calculate slice boundaries
                ye = min(y + th, h)
                xe = min(x + tw, w)
                
                # Extract tile
                tile = grid[y:ye, x:xe]
                
                # Apply compute (e.g. convolution, SDF math, filters)
                processed_tile = compute_func(tile)
                
                # Reinsert into output
                output[y:ye, x:xe] = processed_tile
                
        return output

if __name__ == "__main__":
    def invert_filter(tile): return 255 - tile
    
    solver = TileSolver(tile_size=(2, 2))
    mock_grid = np.zeros((4, 4), dtype=np.uint8)
    result = solver.solve_grid(mock_grid, invert_filter)
    print(result)
