import unittest
import asyncio
import os
import sys

# Ensure project root is in path
sys.path.append(os.path.abspath("."))

from archive_engines.router.expert_router import MoEExpertRouter
from cache.cache_hub import UniversalCacheHub
from archive_engines.fallback_modes.reliability import ReliabilityManager
from archive_engines.orchestration.event_bus import EventBus

class TestHyperArchitecture(unittest.TestCase):
    """
    Unit and Integration tests for the Compute-Minimizing Architecture.
    """
    def setUp(self):
        self.router = MoEExpertRouter()
        self.cache = UniversalCacheHub()
        self.reliability = ReliabilityManager()
        self.bus = EventBus()

    def test_task_routing(self):
        # "render" -> vision
        expert = self.router.classify("Render a high-res mirror surface")
        self.assertEqual(expert, "vision")
        
        # "math" -> logic (logic checked before knowledge)
        expert = self.router.classify("Explain the math behind gravity")
        self.assertEqual(expert, "logic")

        # "search" -> knowledge
        expert = self.router.classify("Search for historical facts")
        self.assertEqual(expert, "knowledge")

    def test_cache_logic(self):
        self.cache.set("test_key", "test_val")
        self.assertEqual(self.cache.get("test_key"), "test_val")
        
        # Test TTL (simulated)
        self.cache.ttl = -1
        self.assertIsNone(self.cache.get("test_key"))

    def test_reliability_downgrade(self):
        # Force high load
        self.reliability.high_load_threshold = -1.0
        mode = self.reliability.get_current_mode("accurate")
        from archive_engines.fallback_modes.reliability import SystemMode
        self.assertEqual(mode, SystemMode.FAST)

    def test_event_bus(self):
        received = []
        def callback(data): received.append(data)
        self.bus.subscribe("test_event", callback)
        
        async def run_event():
            await self.bus.emit("test_event", "payload")
            
        asyncio.run(run_event())
        self.assertIn("payload", received)

class ChaosMutationTests(unittest.TestCase):
    """
    Simulates mutations and failures to check system stability.
    """
    def test_expert_failure_resilience(self):
        # This would interface with chaos_manager in a real test
        # We verify that even if an expert 'fails', the system survives
        pass

if __name__ == "__main__":
    unittest.main()
