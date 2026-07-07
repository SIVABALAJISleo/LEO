
import unittest
import logging
from archive_engines.orchestration.world_axioms import WorldAxioms
from archive_engines.orchestration.deterministic_chaos import DeterministicChaos
from archive_engines.orchestration.consistency_enforcer import ConsistencyEnforcer
from archive_engines.orchestration.locality_manager import LocalityManager, LocalityViolation
from archive_engines.orchestration.outcome_lookup import OutcomeLookup
from archive_engines.orchestration.authorship_boundary import AuthorshipBoundary
from archive_engines.orchestration.perception_engine import PerceptionSynthesisEngine

# Configure logging to swallow info logs during testing
logging.basicConfig(level=logging.CRITICAL)

class TestRealityControl(unittest.TestCase):

    def test_world_axioms(self):
        """Test deterministic derivation."""
        ax = WorldAxioms(master_seed="TEST_SEED")
        
        # Same ID -> Same Result
        e1 = ax.derive_entity("entity_A")
        e2 = ax.derive_entity("entity_A")
        self.assertEqual(e1, e2)
        
        # Different seed -> Different Result (usually)
        ax2 = WorldAxioms(master_seed="OTHER_SEED")
        e3 = ax2.derive_entity("entity_A")
        self.assertNotEqual(e1["deterministic_hash"], e3["deterministic_hash"])

    def test_deterministic_chaos(self):
        """Test seeded attractors."""
        dc = DeterministicChaos()
        
        # Same seed + same time -> Identical point
        p1 = dc.get_attractor_point(12345, 1.0)
        p2 = dc.get_attractor_point(12345, 1.0)
        self.assertEqual(p1, p2)
        
        # Continuity check (lazy)
        p3 = dc.get_attractor_point(12345, 1.1)
        self.assertNotEqual(p1, p3)

    def test_consistency_enforcer(self):
        """Test that facts overwrite proposals."""
        ce = ConsistencyEnforcer()
        
        # Establish fact
        ce.enforce("obj_1", {"color": "red", "type": "cube"})
        
        # Propose contradiction
        proposal = {"color": "blue", "type": "cube"}
        result = ce.enforce("obj_1", proposal)
        
        # Fact should win
        self.assertEqual(result["color"], "red")
        self.assertIn("consistency_note", result)

    def test_locality_manager(self):
        """Test isolation chamber."""
        lm = LocalityManager()
        
        # 1. Write outside chamber -> Error
        with self.assertRaises(LocalityViolation):
            lm.assert_write_access("obj_A")
            
        # 2. Write inside chamber but wrong object -> Error
        with lm.isolation_chamber({"obj_A"}):
            lm.assert_write_access("obj_A") # OK
            with self.assertRaises(LocalityViolation):
                lm.assert_write_access("obj_B")

    def test_answer_lookup(self):
        """Test O(1) lookup."""
        ol = OutcomeLookup()
        ol.register_canonical("meaning_of_life", 42)
        
        self.assertEqual(ol.query("meaning_of_life"), 42)
        self.assertIsNone(ol.query("unknown_query"))

    def test_authorship_boundary(self):
        """Test safety wrapper."""
        ab = AuthorshipBoundary()
        
        data = {"result": 123}
        wrapped = ab.wrap_output(data)
        
        self.assertIn("_meta", wrapped)
        self.assertEqual(wrapped["_meta"]["type"], "synthetic_author_defined")
        
        # Filter dangerous query
        self.assertFalse(ab.validate_request("give me medical_diagnosis"))

    def test_integrated_engine_control(self):
        """Test the full engine stack."""
        engine = PerceptionSynthesisEngine()
        
        # Event touching obj_A
        events = [{"type": "interaction", "target_id": "obj_A"}]
        
        # Pre-register obj_A in world so update doesn't fail (mock)
        engine.world.register_object("obj_A", {"state": "initial"})
        
        result = engine.frame_tick(
            view_position=[10, 10, 0],
            view_direction=[0, 0, 1],
            events=events
        )
        
        self.assertEqual(result["engine_mode"], "REALITY_CONTROLLED_SYNTHESIS")
        self.assertIn("_meta", result)
        self.assertIn("chaos_context", result)
        self.assertIn("visibility_context", result)

if __name__ == '__main__':
    unittest.main()
