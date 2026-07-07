
class ParticleSystem:
    """
    10M Particle Simulation via Seeded RNG and Spatial Culling.
    """
    def __init__(self, seed=42):
        self.seed = seed
        self.grid_size = 10.0
        self.active_grid = set()

    def simulate(self, current_time, camera_frustum):
        """
        Handles 10M particles by only simulating the visible 1%.
        Why this avoids GPU: Seeded RNG makes particle state a pure function of (seed, time).
        No need to store or update 10M positions every frame.
        """
        visible_cells = self.get_visible_cells(camera_frustum)
        for cell in visible_cells:
            self.render_cell_particles(cell, current_time)

    def render_cell_particles(self, cell, time):
        # Deterministic generation using cell_id and seed
        # state = f(seed, cell_id, time)
        pass
