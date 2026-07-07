import time
import json
import logging
from typing import Dict, Any
from fastapi import FastAPI
from fastapi.responses import StreamingResponse

# OS Core Components
from archive_engines.llm_os_core.memory_knowledge import OSMemory, OSKnowledge
from archive_engines.llm_os_core.execution import ExecutionLoop
from intel_core_ai.inference import IntelInferenceEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="LLM Operating System (Production Core)")

# Init Kernel
model_path = "models/phi-3-mini-4k-instruct-q4_k_m.gguf"
inference = IntelInferenceEngine(model_path)
memory = OSMemory()
knowledge = OSKnowledge()
execution_loop = ExecutionLoop(inference, memory, knowledge)

# Seed Knowledge
knowledge.add_docs([
    "The LLM OS kernel manages reasoning steps like a CPU manages threads.",
    "Context Memory (RAM) allows small models to persist state across complex tasks.",
    "Validation passes prevent hallucinatory output in local AI systems."
])

@app.post("/os_kernel_query")
async def handle_kernel_query(raw_input: Dict[str, Any]):
    """
    LAYER 1: LLM OS LOOP
    """
    start_time = time.time()
    query = raw_input.get("query", "")
    memory.reset()
    
    async def run_os_kernel():
        # 1. Perception & ACK (Layer 8)
        yield json.dumps({"status": "ACK", "kernel": "Booting reasoning loop...", "t": f"{(time.time()-start_time)*1000:.1f}ms"})

        # 2. Intent Collapse & Decomposition (Layer 1 & 7)
        # Convert query to structured intent
        parse_prompt = "Decompose this query into 2-3 logical steps. Output JSON list of strings only."
        gen = inference.generate_stream(query, parse_prompt)
        res = "".join(list(gen))
        try:
            steps = json.loads(res[res.find("["):res.rfind("]")+1])
        except:
            steps = ["Analyze input", "Generate response"]
        
        memory.scratchpad["goal"] = query
        memory.scratchpad["steps"] = steps
        yield json.dumps({"step": "KERNEL_DECOMPOSE", "tasks": steps})

        # 3. Execution Loop (Layer 2)
        for i, task in enumerate(steps):
            yield json.dumps({"step": f"EXECUTION_{i+1}", "task": task})
            result = await execution_loop.solve_step(task, query)
            yield json.dumps({"step": f"STEP_{i+1}_COMPLETE", "result": result[:200] + "..."})

        # 4. Synthesis & Output (Layer 10)
        yield json.dumps({"step": "SYNTHESIS", "msg": "Finalizing kernel output..."})
        ram = memory.get_context_ram()
        final_prompt = f"Synthesize a final response based on this RAM state:\n{ram}"
        
        full_final = ""
        for token in inference.generate_stream(query, final_prompt):
            full_final += token
            yield json.dumps({"token": token})

        yield json.dumps({"step": "HALT", "latency": f"{(time.time()-start_time)*1000:.1f}ms"})

    return StreamingResponse(run_os_kernel(), media_type="application/x-ndjson")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8009)
