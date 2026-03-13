
import unittest
import logging
from orchestration.visibility_manager import VisibilityManager, VisibilityRegionType
from orchestration.specular_governor import SpecularGovernor
from orchestration.chaos_containment import ChaosContainment
from orchestration.lazy_world import LazyWorldManager

# Configure logging to swallow info logs during testing
logging.basicConfig(level=logging.CRITICAL)

class TestPerceptionSynthesis(unittest.TestCase):

    def test_generative_visibility_fill(self):
        """Test that unknown regions are instantly generated."""
        vm = VisibilityManager()
        
        # Request a truly unknown region
        result = vm.request_visibility("region_xyz_123")
        
        self.assertEqual(result["compute_type"], "generative_infill")
        self.assertIn("generated_texture", result["appearance"])
        self.assertEqual(vm._visibility_map["region_xyz_123"], VisibilityRegionType.GENERATED)
        
        # Request again -> should be cache hit
        result2 = vm.request_visibility("region_xyz_123")
        self.assertEqual(result2["compute_type"], "generative_cache_hit")

    def test_view_dependent_light_lookup(self):
        """Test O(1) light field lookup."""
        sg = SpecularGovernor()
        
        # Test finding a value
        color = sg.query_specular_field([0.5, 0.5, 0.5], [1.0, 0.0, 0.0])
        self.assertEqual(len(color), 3)
        
        # Test evaluation shortcut
        rays = [{"origin": [0,0,0], "direction": [0,1,0], "energy": 1.0}]
        result = sg.evaluate_path(rays, use_learned_field=True)
        
        self.assertEqual(result["status"], "lookup_hit")
        self.assertEqual(result["governance_note"], "O(1) Light Field Lookup Used")
        self.assertEqual(result["final_depth"], 0)

    def test_pattern_based_physics(self):
        """Test snapping chaotic systems to valid patterns."""
        cc = ChaosContainment(lyapunov_threshold=0.5)
        
        # Stable system -> Deterministic
        res_stable = cc.analyze_trajectory(initial_state=0.0, time_steps=10, lyapunov_exponent=0.1)
        self.assertEqual(res_stable["mode"], "DETERMINISTIC_TRAJECTORY")
        
        # Chaotic system -> Pattern Playback (NOT statistical envelope anymore, as per new rule)
        res_chaotic = cc.analyze_trajectory(initial_state=0.5, time_steps=10, lyapunov_exponent=0.9)
        self.assertEqual(res_chaotic["mode"], "PATTERN_PLAYBACK")
        self.assertIn("trajectory", res_chaotic)

    def test_lazy_world_update(self):
        """Test that only touched objects update."""
        lw = LazyWorldManager()
        
        # Register two objects
        lw.register_object("obj_1", {"energy": 100})
        lw.register_object("obj_2", {"energy": 100})
        
        # Tick 1: No touches -> No updates
        res1 = lw.update()
        self.assertEqual(res1["updated_count"], 0)
        self.assertEqual(lw.get_state("obj_1")["energy"], 100)
        
        # Tick 2: Touch obj_1
        lw.touch_object("obj_1")
        res2 = lw.update()
        
        self.assertEqual(res2["updated_count"], 1)
        self.assertIn("obj_1", res2["updates"])
        self.assertNotIn("obj_2", res2["updates"])
        
        # Obj 1 should have evolved (energy -1.0)
        self.assertEqual(lw.get_state("obj_1")["energy"], 99.0)
        # Obj 2 remains frozen
        self.assertEqual(lw.get_state("obj_2")["energy"], 100.0)

if __name__ == '__main__':
    unittest.main()
