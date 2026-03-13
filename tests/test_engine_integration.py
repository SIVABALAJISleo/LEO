
import unittest
import logging
from orchestration.perception_engine import PerceptionSynthesisEngine

# Configure logging to swallow info logs during testing
logging.basicConfig(level=logging.CRITICAL)

class TestPerceptionEngineIntegration(unittest.TestCase):

    def test_engine_tick(self):
        """Test the unified engine tick."""
        engine = PerceptionSynthesisEngine()
        
        # Test a tick with an interaction
        result = engine.frame_tick(
            view_position=[10.5, 20.2, 0.0],
            view_direction=[0.0, 0.0, 1.0],
            events=[{"type": "interaction", "target_id": "obj_A"}]
        )
        
        self.assertEqual(result["engine_mode"], "PERCEPTION_SYNTHESIS")
        self.assertIn("world_status", result)
        self.assertIn("visibility_context", result)
        self.assertIn("ambient_light", result)
        
        # Visibility should be for the "inferred" region
        self.assertEqual(result["visibility_context"]["region_id"], "region_10_20")
        
        # Light should have 3 components
        self.assertEqual(len(result["ambient_light"]), 3)

if __name__ == '__main__':
    unittest.main()
