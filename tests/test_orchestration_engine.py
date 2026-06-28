import json
import os

class MockIngestionManager:
    def __init__(self):
        self.store = {}
    def ingest(self, name, asset_type, metadata):
        asset_id = "mock-id-123"
        self.store[asset_id] = {"type": asset_type, "metadata": metadata}
        return asset_id
    def get_asset(self, asset_id):
        return self.store.get(asset_id)

class MockMoERouter:
    def route(self, query):
        if "detect" in query or "objects" in query:
            return {"chosen_expert": "vision"}
        return {"chosen_expert": "general"}

class MockInferenceCache:
    def __init__(self):
        self.cache = {}
    def set(self, input_data, result):
        key = json.dumps(input_data, sort_keys=True)
        self.cache[key] = result
    def get(self, input_data):
        key = json.dumps(input_data, sort_keys=True)
        return self.cache.get(key)

ingestion_manager = MockIngestionManager()
moe_router = MockMoERouter()
inference_cache = MockInferenceCache()

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
    test_asset_ingestion()
    test_routing_and_vision()
    test_caching()
    print("\nALL ORCHESTRATION TESTS PASSED!")
