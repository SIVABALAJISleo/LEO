"""
hyper/integrations/blender/HyperBlender/lod/adaptive_lod.py
"""
class BlenderAdaptiveLOD:
    """Manages Subdivision Surface and Decimate modifier levels dynamically based on camera distance."""
    def get_modifier_levels(self, distance: float) -> int:
        if distance < 5.0:
            return 2  # high viewport subsurf
        elif distance < 20.0:
            return 1  # mid subsurf
        else:
            return 0  # base mesh
