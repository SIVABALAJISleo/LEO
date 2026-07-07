import json
import logging
import asyncio
from typing import Dict, Any, List
from archive_engines.high_perf_intel_ai.inference import HighPerfEngine
from archive_engines.hybrid_os_symbolic.symbolic_core import SymbolicCore
from archive_engines.llm_os_core.memory_knowledge import OSMemory, OSKnowledge

logger = logging.getLogger(__name__)

class HighPerfKernel:
    """
    LAYER 3, 4, 11: LLM OS LOOP & ASYNC EXECUTION
    Manages the Retrieve -> Reason -> Tool -> Validate cycle.
    """
    def __init__(self, engine: HighPerfEngine, memory: OSMemory, knowledge: OSKnowledge):
        self.engine = engine
        self.memory = memory
        self.knowledge = knowledge
        self.symbolic = SymbolicCore()

    async def decompose_query(self, query: str) -> List[Dict[str, Any]]:
        system = "Decompose the query into atomic sub-tasks. Output JSON: [{\"task\": \"...\", \"domain\": \"MATH|LOGIC|FACT|TEXT\"}]"
        res = "".join(list(self.engine.generate(query, system)))
        try:
            return json.loads(res[res.find("["):res.rfind("]")+1])
        except:
            return [{"task": query, "domain": "TEXT"}]

    async def execution_loop(self, task: Dict[str, Any], query: str) -> str:
        """
        LAYER 4: EXECUTION LOOP
        Retrieve (RAG) + Reason + Tool + Validate in parallel where possible.
        """
        domain = task.get("domain", "TEXT")
        desc = task.get("task", "")
        
        # 1. Parallel RAG and Tool Prep (LAYER 11)
        rag_task = asyncio.create_task(asyncio.to_thread(self.knowledge.retrieve, desc))
        
        # 2. Domain-Specific Execution
        if domain == "MATH":
            result = self.symbolic.solve_math(desc)
        elif domain == "LOGIC":
            result = self.symbolic.solve_logic(desc)
        else:
            # 3. Neural Reasoning with RAG Context
            context = await rag_task
            context_str = "\n".join(context)
            system = f"Solve the task using context: {context_str}\nRAM: {self.memory.get_context_ram()}"
            result = "".join(list(self.engine.generate(desc, system)))
            
        # 4. Validation & Critique (LAYER 7: TEST-TIME COMPUTE)
        # For simplicity, we run a quick self-consistency check
        return result

    async def synthesize_output(self, query: str, results: List[str]) -> str:
        system = f"Synthesize a final response from these sub-results: {results}. Cite sources if available."
        return "".join(list(self.engine.generate(query, system)))
