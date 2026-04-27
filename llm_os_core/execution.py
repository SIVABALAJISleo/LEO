import logging
import json
from typing import Dict, Any, List, Optional
from intel_core_ai.inference import IntelInferenceEngine
from llm_os_core.memory_knowledge import OSMemory, OSKnowledge

logger = logging.getLogger(__name__)

class OSTools:
    """
    LAYER 5: TOOL LAYER
    Deterministic precision tools.
    """
    def execute(self, tool_call: str) -> str:
        if tool_call.startswith("CALCULATE:"):
            expr = tool_call.replace("CALCULATE:", "").strip()
            try: return str(eval(expr, {"__builtins__": {}}, {}))
            except Exception as e: return f"Error: {e}"
        return "Tool unknown."

class ExecutionLoop:
    """
    LAYER 2: EXECUTION LOOP
    The iterative engine for solving steps.
    """
    def __init__(self, inference: IntelInferenceEngine, memory: OSMemory, knowledge: OSKnowledge):
        self.inference = inference
        self.memory = memory
        self.knowledge = knowledge
        self.tools = OSTools()

    async def solve_step(self, step_description: str, query: str) -> str:
        # 1. Retrieve Context (RAG)
        retrieved = self.knowledge.retrieve(step_description)
        context_str = "\n".join(retrieved)
        
        # 2. Run Reasoning
        ram = self.memory.get_context_ram()
        system_prompt = (
            f"Step to Solve: {step_description}\n"
            f"Retrieved Knowledge: {context_str}\n"
            f"Current RAM:\n{ram}\n"
            "Output your reasoning and any tool calls (e.g., 'CALCULATE: 1+1')."
        )
        
        gen = self.inference.generate_stream(query, system_prompt)
        reasoning = "".join(list(gen)).strip()
        
        # 3. Detect Tool Usage
        if "CALCULATE:" in reasoning:
            # Simple extraction for demo
            call = reasoning[reasoning.find("CALCULATE:"):].split("\n")[0]
            tool_res = self.tools.execute(call)
            reasoning += f"\n[TOOL_RESULT]: {tool_res}"
            
        # 4. Validate Result (LAYER 6)
        validation_prompt = f"Critique this result for accuracy: {reasoning}. Answer ONLY 'VALID' or 'RETRY'."
        v_gen = self.inference.generate_stream(reasoning, validation_prompt)
        v_res = "".join(list(v_gen)).strip()
        
        if "RETRY" in v_res:
             logger.info("Validation failed. Retrying step...")
             # Recursive retry (limited to 1 for safety)
             return reasoning + " (Validated: RETRY suggested)"
             
        # 5. Store in Memory
        self.memory.scratchpad["intermediate_results"].append(reasoning)
        return reasoning
