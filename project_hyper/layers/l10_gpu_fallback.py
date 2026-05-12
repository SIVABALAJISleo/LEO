import asyncio

class GPUFallback:
    """
    Layer 8: Optional GPU Fallback
    External API call (OpenAI/Cloud GPU). Used only in rare cases.
    """
    def __init__(self, api_key: str = "OPTIONAL"):
        self.api_key = api_key

    async def generate_async(self, query: str) -> str:
        """Simulates an external GPU-backed API call."""
        print("[L8] Triggering External GPU API Fallback...")
        await asyncio.sleep(1.0) # Simulate network latency
        return f"[EXTERNAL GPU RESPONSE] for: {query}"

if __name__ == "__main__":
    fallback = GPUFallback()
    asyncio.run(fallback.generate_async("Solve the P vs NP problem"))
