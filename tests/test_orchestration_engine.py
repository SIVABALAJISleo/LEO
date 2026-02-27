import json
import os
from backend.main import ingestion_manager, moe_router, inference_cache

def test_asset_ingestion():
    print("Testing Asset Ingestion...")
    asset_id = ingestion_manager.ingest("test_image.png", "image", {"resolution": "1920x1080"})
    asset = ingestion_manager.get_asset(asset_id)
    assert asset["type"] == "image"
    assert asset["metadata"]["resolution"] == "1920x1080"
    print(f"✓ Ingested asset: {asset_id}")

def test_routing_and_vision():
    print("Testing Routing and Vision...")
    query = "detect objects in this frame"
    route_result = moe_router.route(query)
    assert route_result["chosen_expert"] == "vision"
    print("✓ Successfully routed to Vision Expert")

def test_caching():
    print("Testing Caching Layer...")
    input_data = {"task": "test", "data": 123}
    result = {"status": "calculated"}
    inference_cache.set(input_data, result)
    cached = inference_cache.get(input_data)
    assert cached == result
    print("✓ Cache working correctly")

if __name__ == "__main__":
    # Create temp files for testing if needed
    if not os.path.exists("data"):
        os.makedirs("data")
        
    try:
        test_asset_ingestion()
        test_routing_and_vision()
        test_caching()
        print("\nALL ORCHESTRATION TESTS PASSED!")
    except Exception as e:
        print(f"\nTEST FAILED: {str(e)}")
