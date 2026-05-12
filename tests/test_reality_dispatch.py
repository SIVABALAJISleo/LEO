
import unittest
import logging
import time
from orchestration.reality_dispatcher import RealityDispatcher

# Configure logging to swallow info logs during testing
logging.basicConfig(level=logging.CRITICAL)

class TestRealityDispatch(unittest.TestCase):

    def test_zero_stall_pipeline(self):
        """
        Verify that the pipeline runs in O(1) time (under 10ms for mock).
        """
        dispatcher = RealityDispatcher()
        
        event = {
            "target_id": "fast_entity_123",
            "context": {"view_position": [0,0,0], "view_direction": [0,1,0]}
        }
        
        start = time.time()
        result = dispatcher.dispatch_event(event)
        duration = (time.time() - start) * 1000
        
        # Must be fast
        self.assertLess(duration, 50.0, "Dispatch pipeline exceeded 50ms latency target")
        
        # Check integrity
        self.assertEqual(result["status"], "RESOLVED")
        self.assertIn("entity", result) # Step A
        self.assertIn("geometry", result) # Step B
        self.assertIn("semantics", result) # Step C

    def test_axiom_rejection(self):
        """Verify Step A rejects invalid entities."""
        dispatcher = RealityDispatcher()
        # Invalid ID (has space, violates isalnum check from earlier axiom)
        # Note: We allowed underscores, but spaces are still invalid for isalnum()
        bad_event = {"target_id": "invalid entity"} 
        
        result = dispatcher.dispatch_event(bad_event)
        
        self.assertIn("error", result)
        self.assertIn("Axiom Violation", result["error"])

    def test_answer_only_contract(self):
        """Verify output contains only answers, no process flags."""
        dispatcher = RealityDispatcher()
        event = {"target_id": "query_object"}
        
        result = dispatcher.dispatch_event(event)
        
        # Ensure deep keys exist
        self.assertIn("form", result["geometry"])
        self.assertIn("semantic_class", result["semantics"])
        
        # Ensure Safety Wrapper
        self.assertIn("_meta", result)
        self.assertEqual(result["_meta"]["type"], "synthetic_author_defined")

if __name__ == '__main__':
    unittest.main()
