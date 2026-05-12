import asyncio
import time
import os
import sys

sys.path.append(os.getcwd())

from backend.core.stability_layer import global_stability_layer

async def test():
    try:
        res = await global_stability_layer.secure_invoke("What is Project HYPER?", "REQ_DEBUG_1", "default", "default")
        print(f"RESULT: {res}")
    except Exception as e:
        import traceback
        print(f"FAILED: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test())
