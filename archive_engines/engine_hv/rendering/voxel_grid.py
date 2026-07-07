import numpy as np

class VoxelGrid:
    """
    Sparse Voxel Grid for Baked Radiance (NanoVDB Style).
    """
    def __init__(self, resolution=(128, 128, 128)):
        self.res = resolution
        # Sparse storage: [index] -> [R, G, B, Density]
        self.data = {} 

    def lookup(self, world_pos):
        """
        O(1) lookup of precomputed lighting.
        Why this avoids GPU: No ray traversal, just array indexing + interpolation.
        """
        grid_pos = self.world_to_grid(world_pos)
        return self.data.get(tuple(grid_pos), np.zeros(4))

    def world_to_grid(self, pos):
        return np.floor(pos).astype(int)

class LightProbeGrid:
    """
    Grid of Spherical Harmonic coefficients for global illumination.
    2m spacing as per requirements.
    """
    def __init__(self, bounds, spacing=2.0):
        self.spacing = spacing
        self.dims = np.ceil((bounds[1] - bounds[0]) / spacing).astype(int)
        # Store 9 SH coefficients per probe for O(1) irradiance lookup
        self.probes = np.zeros((*self.dims, 9, 3)) 

    def get_irradiance(self, pos, normal):
        """
        Uses SH coefficients to compute irradiance in O(1).
        Why this avoids GPU: Complex GI is pre-integrated into SH coefficients.
        """
        sh_basis = self.compute_sh_basis(normal)
        coefficients = self.interpolate_probes(pos)
        return np.dot(sh_basis, coefficients)
