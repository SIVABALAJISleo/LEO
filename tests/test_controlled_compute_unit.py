"""
tests/test_controlled_compute_unit.py
Unit test for Controlled Compute logic in ZeroComputeControl.
"""
import sys
import os
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.core.zero_compute import global_zero_control

async def test_logic():
    print("Testing ZeroComputeControl Logic...")
    
    # Mock dependencies to avoid timeouts
    with patch('backend.shadow.shadow_store.global_shadow_store.lookup', return_value=None), \
         patch('backend.intelligence.delta_engine.global_delta_engine_v2.find_delta', return_value=None), \
         patch('backend.optimization.soft_match.global_soft_match.find_match', return_value=None), \
         patch('backend.runtime.composer.global_runtime_composer.compose_response', return_value=None), \
         patch('backend.optimization.heat_scheduler.global_heat_scheduler.should_skip_heavy_logic', return_value=False), \
         patch('backend.optimization.compute_budget.global_compute_budget.has_capacity', return_value=True), \
         patch('backend.background.compute_engine.global_bg_compute.enqueue', new_callable=AsyncMock):
        
        # Test 1: High Priority (how_to)
        query = "What are the steps to install hyper?"
        print(f"\n[Unit Test 1] High Priority Execution: '{query}'")
        res = await global_zero_control.handle_request(query, "req_001", "t1", "w1", 1000.0)
        print(f"  -- Mode: {res.get('mode')}")
        assert res.get('mode') == "SYMBOLIC", f"EXPECTED SYMBOLIC, GOT {res.get('mode')}"

        # Test 2: Low Priority (information)
        query2 = "What is the capital of France?"
        print(f"\n[Unit Test 2] Low Priority Fallback: '{query2}'")
        res2 = await global_zero_control.handle_request(query2, "req_002", "t1", "w1", 1000.0)
        print(f"  -- Mode: {res2.get('mode')}")
        assert res2.get('mode') == "SYMBOLIC", f"EXPECTED SYMBOLIC, GOT {res2.get('mode')}"

    print("\n✅ CONTROLLED COMPUTE UNIT TESTS PASSED.")

if __name__ == "__main__":
    asyncio.run(test_logic())
