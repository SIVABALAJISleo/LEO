import sys
import os

# Ensure the root directory is in sys.path for absolute imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.input_logic import parse_input
from execution.reasoning_loop import start_loop
from archive_engines.verifier.validation import validate_output
from archive_engines.router.routing_logic import get_compute_node
from memory.knowledge import resolve_entity

from core_ai.hyperdimensional.resonance_cache import ResonanceCache
from core_ai.hyperdimensional.crystallizer import StateCrystallizer
import time

# Initialize HDC singletons
hdc_cache = ResonanceCache(threshold=0.3)
hdc_crystallizer = StateCrystallizer()

def run_system(user_query: str):
    print(f"--- HYPER AI SYSTEM START ---")
    t0 = time.perf_counter()
    
    # [HDC INTERCEPTION]
    is_hit, response = hdc_cache.check_resonance(user_query)
    if is_hit:
        elapsed = (time.perf_counter() - t0) * 1000
        print(f"[HDC Cache Hit] {elapsed:.2f}ms")
        print(f"Response: {response}")
        print(f"--- SYSTEM SHUTDOWN ---")
        return response
        
    print("[HDC Cache Miss] Routing to Non-Autoregressive Crystallizer...")
    response = hdc_crystallizer.generate_response(user_query)
    
    # Save to cache for next time
    hdc_cache.update_cache(user_query, response)
    
    elapsed = (time.perf_counter() - t0) * 1000
    print(f"[HDC Crystallizer] Generated in {elapsed:.2f}ms")
    print(f"Response: {response}")
    print(f"--- SYSTEM SHUTDOWN ---")
    return response

    # 1. Route Compute
    node = get_compute_node(0.1)
    print(f"Routing to: {node}")
    
    # 2. Resolve Entity
    entity_type = resolve_entity("NVIDIA")
    print(f"Entity Resolved: {entity_type}")
    
    # 3. Parse Input
    parsed = parse_input(user_query)
    print(f"Input Parsed: {parsed}")
    
    # 4. Execute Reasoning Loop
    results = start_loop(user_query, steps=2)
    print(f"Reasoning Complete: {results}")
    
    # 5. Verify Results
    final_result = results[-1]["result"]
    is_valid = validate_output(final_result)
    print(f"Verification: {'PASS' if is_valid else 'FAIL'}")
    
    print(f"--- SYSTEM SHUTDOWN ---")

if __name__ == "__main__":
    query = "Optimize compute for NVIDIA"
    run_system(query)
