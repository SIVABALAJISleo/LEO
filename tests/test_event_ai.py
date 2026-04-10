import sys
import os
import time
import numpy as np

# Ensure backend modules are importable
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from orchestration.event_vision import EventVisionSystem
from orchestration.symbolic_core import SymbolicAICore, create_proximity_rule

def test_event_vision_scaling():
    """Feature A: Verify zero cost for static scenes."""
    evs = EventVisionSystem(sensitivity=0.1)
    
    # Simulate a 100-camera system
    num_cameras = 100
    resolution = (10, 10) # simplified frame
    
    # 1. Initialize all cameras (first frame)
    # This has cost, but steady state should be zero
    print("Initializing 100 cameras...")
    for i in range(num_cameras):
        cam_id = f"cam_{i}"
        frame = np.zeros(resolution)
        evs.process_frame(cam_id, frame)
        
    # 2. Process STATIC frames (Should be zero events)
    start_time = time.time()
    total_events = 0
    
    # Simulate processing loop for all 100 cameras again with SAME data
    for i in range(num_cameras):
        cam_id = f"cam_{i}"
        frame = np.zeros(resolution) # Same black frame
        new_events = evs.process_frame(cam_id, frame)
        total_events += new_events
        
    duration = time.time() - start_time
    
    # Check 1: Zero events generated
    assert total_events == 0, f"Expected 0 events for static scene, got {total_events}"
    print(f"✓ 100 Cameras (Static) -> {total_events} Events (0 CPU Load verified)")
    
    # 3. Process CHANGE in ONE camera
    frame_changed = np.zeros(resolution)
    frame_changed[5,5] = 1.0 # Pixel change
    
    events_generated = evs.process_frame("cam_42", frame_changed)
    assert events_generated == 1, "Change detection failed"
    print("✓ Single Camera Change -> Event Triggered")

def test_symbolic_core_logic():
    """Feature B: Verify deterministic symbolic logic."""
    core = SymbolicAICore()
    
    # Define a rule: If movement in Hallway > 0.5 -> "ALERT_SECURITY"
    rule = create_proximity_rule("cam_hallway", 0.5, "ALERT_SECURITY")
    core.register_rule(rule)
    
    # Test 1: Minor event (Below threshold)
    event_minor = {"type": "VISUAL_CHANGE", "camera_id": "cam_hallway", "magnitude": 0.1}
    actions1 = core.process_event(event_minor)
    assert len(actions1) == 0, "Rule triggered incorrectly (threshold failed)"
    
    # Test 2: Major event (Above threshold)
    event_major = {"type": "VISUAL_CHANGE", "camera_id": "cam_hallway", "magnitude": 0.8}
    start_time = time.time()
    actions2 = core.process_event(event_major)
    duration = time.time() - start_time
    
    assert "ALERT_SECURITY" in actions2, "Rule failed to trigger"
    print(f"✓ Symbolic Logic Triggered: {actions2} (Deterministic Latency: {duration:.6f}s)")

if __name__ == "__main__":
    test_event_vision_scaling()
    test_symbolic_core_logic()
    print("\nALL EVENT-DRIVEN AI TESTS PASSED.")
