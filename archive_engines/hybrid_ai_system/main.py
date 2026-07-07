from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
import logging

from archive_engines.hybrid_ai_system.services.vector_db import UnifiedVectorDB
from archive_engines.hybrid_ai_system.services.model_manager import HybridModelManager
from archive_engines.hybrid_ai_system.services.verifier_engine import VerifierEngine
from archive_engines.hybrid_ai_system.core.router import HybridRouter, Route
from archive_engines.hybrid_ai_system.core.open_logic import OpenSystem
from archive_engines.hybrid_ai_system.core.closed_logic import ClosedSystem

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("HybridAISystem")

app = FastAPI(title="Hybrid AI System: Open/Closed")

# Initialize Shared Services
db = UnifiedVectorDB("data/hybrid_cache/index.faiss", "data/hybrid_cache/metadata.json")
models = HybridModelManager()
verifier = VerifierEngine()

# Initialize Core Logic
router = HybridRouter()
open_sys = OpenSystem(models)
closed_sys = ClosedSystem(models, verifier)

class HybridRequest(BaseModel):
    task: str
    constraints: Optional[str] = ""
    tests: Optional[str] = ""
    force_verify: bool = False

@app.post("/solve")
async def solve_task(request: HybridRequest):
    # 6. CACHE (ZERO COMPUTE)
    cached = await db.search(request.task)
    if cached:
        logger.info("ZERO COMPUTE: Cache hit.")
        return {"result": cached["response"], "source": "cache", "confidence": 1.0}

    # 1. INPUT (Simplified intent extraction)
    intent = "code" if request.tests else "general"
    
    # 3. ROUTER
    route = Route.CLOSED if request.force_verify else router.route(intent, request.task)
    logger.info(f"ROUTING: {route}")

    if route == Route.OPEN:
        # 2. OPEN SYSTEM
        candidates = await open_sys.propose(request.task, request.constraints)
        result = candidates[0]
        return {"result": result, "source": "open", "verified": False}
    else:
        # 4. CLOSED SYSTEM
        verified_result = await closed_sys.run_loop(
            request.task, request.constraints, request.tests
        )
        
        if verified_result:
            # 6. STORE IN CACHE
            await db.store(request.task, verified_result, {"type": "verified"})
            return {"result": verified_result, "source": "closed", "verified": True}
        else:
            # 8. OUTPUT CONTROL
            return {
                "result": None, 
                "source": "closed", 
                "status": "failed_verification", 
                "message": "Could not generate verified output."
            }

@app.get("/health")
async def health():
    return {"status": "ready", "hybrid_mode": True, "cpu_optimized": True}
