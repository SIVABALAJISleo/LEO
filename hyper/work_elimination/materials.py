"""
hyper/work_elimination/materials.py
===================================
HYPER Material & Shader Elimination:
Classifies materials, prunes redundant shader permutations, and manages texture residency.
"""

from typing import Any, Dict, List, Set


class MaterialEliminationEngine:
    """
    Minimizes shader switching overhead and optimizes texture residency.
    """

    def __init__(self):
        self.shader_cache: Dict[str, Any] = {}
        self.compiled_permutations: Set[str] = set()

    def classify_material(self, mat_props: Dict[str, Any]) -> str:
        """
        Groups materials into canonical shader classes to avoid permutation explosion.
        Classes: 'unlit', 'diffuse_only', 'standard_pbr', 'complex_translucent'
        """
        is_translucent = mat_props.get("is_translucent", False)
        has_normal_map = mat_props.get("has_normal_map", False)
        has_roughness_metallic = mat_props.get("has_roughness_metallic", True)
        is_emissive = mat_props.get("emissive_intensity", 0.0) > 0.0

        if is_translucent:
            return "complex_translucent"
        if not has_normal_map and not has_roughness_metallic and not is_emissive:
            return "diffuse_only"
        return "standard_pbr"

    def reduce_permutations(self, requested_features: List[str]) -> str:
        """
        Canonicalizes feature flags into minimal compiled shader variants.
        """
        clean_features = sorted(list(set(requested_features)))
        perm_key = "_".join(clean_features) if clean_features else "base"
        self.compiled_permutations.add(perm_key)
        return perm_key
