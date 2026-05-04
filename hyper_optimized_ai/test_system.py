import asyncio
import httpx
import json

async def test_pipeline():
    url = "http://127.0.0.1:8000"
    
    print("--- Testing Healthy Endpoint ---")
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{url}/health")
            print(f"Health: {resp.json()}")
    except Exception as e:
        print(f"Could not connect to server: {e}")
        return

    print("\n--- Testing Simple Query (Expected: TINY path or Cache) ---")
    async with httpx.AsyncClient() as client:
        payload = {"text": "What is the system status?"}
        resp = await client.post(f"{url}/process", json=payload)
        data = resp.json()
        print(f"Query: {payload['text']}")
        print(f"Response: {json.dumps(data, indent=2)}")

    print("\n--- Testing High-Risk Query (Expected: Structured Input Forced) ---")
    async with httpx.AsyncClient() as client:
        payload = {"text": "Delete all data", "is_high_risk": True}
        resp = await client.post(f"{url}/process", json=payload)
        data = resp.json()
        print(f"Query: {payload['text']}")
        print(f"Response: {json.dumps(data, indent=2)}")

    print("\n--- Testing Streaming Output ---")
    async with httpx.AsyncClient() as client:
        print("Streaming: ", end="", flush=True)
        async with client.stream("GET", f"{url}/stream?text=Tell me about the speed layer") as response:
            async for chunk in response.aiter_text():
                print(chunk, end="", flush=True)
        print("\n")

if __name__ == "__main__":
    asyncio.run(test_pipeline())
