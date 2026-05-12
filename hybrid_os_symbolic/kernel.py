import time
import logging
from typing import Dict, Any, List
from hybrid_os_symbolic.symbolic_core import SymbolicCore
from hybrid_os_symbolic.router import HybridRouter
from llm_os_core.memory_knowledge import OSMemory, OSKnowledge
from intel_core_ai.inference import IntelInferenceEngine

logger = logging.getLogger(__name__)

class HybridKernel:
    """
    LAYER 1: CONTROL (LLM OS LOOP)
    LAYER 7: EXECUTION LOOP
    """
    def __init__(self, inference: IntelInferenceEngine, memory: OSMemory, knowledge: OSKnowledge):
        self.inference = inference
        self.memory = memory
        self.knowledge = knowledge
        self.symbolic = SymbolicCore()
        self.router = HybridRouter(inference)

    async def execute_step(self, query: str) -> str:
        # 1. Retrieve Context
        ram = self.memory.get_context_ram()
        
        # 2. Route & Translate (Translator Mode)
        decision = self.router.route_and_translate(query, ram)
        domain = decision.get("domain")
        tool_input = decision.get("tool_input")
        
        # 3. Call Tool (Symbolic Layer)
        raw_result = ""
        if domain == "MATH":
            raw_result = self.symbolic.solve_math(tool_input)
        elif domain == "LOGIC":
            raw_result = self.symbolic.solve_logic(tool_input)
        elif domain == "FACTUAL":
            facts = self.knowledge.retrieve(query)
            raw_result = "\n".join(facts)
        else:
            # Creative / Open - LLM handles
            gen = self.inference.generate_stream(query, "Provide a creative response.")
            raw_result = "".join(list(gen))
            
        # 4. Translate Output
        final_text = self.router.translate_output(raw_result, query)
        
        # 5. Validate & Store
        self.memory.scratchpad["intermediate_results"].append(final_text)
        return final_text
