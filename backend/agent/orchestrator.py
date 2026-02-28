"""
Autonomous Self-Healing Agent Core
Built with LangGraph to orchestrate cyclic loops of error detection, reasoning, and patching.
This module links into the local LlmCpuInferenceEngine as its central intelligence.
"""

import logging
from typing import Dict, Any, List

# LangGraph dependencies (installed via pip)
from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict

# Local internal engine imports
from backend.engine.llm_cpu_inference import LlmCpuInferenceEngine

logger = logging.getLogger(__name__)

# ── 1. Define the Agent's Memory State ─────────────────────────────────────────
class AgentState(TypedDict):
    """
    A Graph State dictionary that holds memory across the autonomous loop.
    """
    error_message: str
    target_file: str
    proposed_code: str
    test_results: str
    attempts: int
    resolved: bool


# ── 2. The Orchestrator Class ──────────────────────────────────────────────────
class AutonomousOrchestrator:
    """
    The main driver behind the self-healing loop.
    It uses a LangGraph finite state machine to loop indefinitely until an error is solved
    or the max trial limit is hit.
    """
    
    def __init__(self, engine: LlmCpuInferenceEngine):
        self.engine = engine
        self.graph = self._build_graph()

    def _build_graph(self):
        """Constructs the cyclic Graph nodes and edges."""
        workflow = StateGraph(AgentState)

        # Map out the autonomous nodes
        workflow.add_node("analyze_error", self.analyze_error_node)
        workflow.add_node("draft_fix", self.draft_fix_node)
        workflow.add_node("apply_and_test", self.apply_and_test_node)

        # Define the routing edges
        workflow.add_edge(START, "analyze_error")
        workflow.add_edge("analyze_error", "draft_fix")
        workflow.add_edge("draft_fix", "apply_and_test")
        
        # Add conditional conditional checks (has it passed?)
        workflow.add_conditional_edges(
            "apply_and_test",
            self.check_resolution_status,
            {
                "success": END,
                "retry": "analyze_error",     # Loop back to start if it failed!
                "failed": END                # Or die gracefully if max retries hit
            }
        )
        
        return workflow.compile()

    # ── Node Implementations ─────────────────

    def analyze_error_node(self, state: AgentState) -> Dict:
        """Reads the error and asks the LLM to find the source."""
        logger.info(f"[Agent] Analyzing Error: {state['error_message']}")
        
        # Simple prompt to the local Llama engine
        prompt = f"Analyze this error and tell me the problem:\n{state['error_message']}"
        # In a real integration, we'd yield/await self.engine.generate(...)
        analysis = "Analysis completed. Attempting fix." 
        
        return {"attempts": state.get("attempts", 0) + 1}

    def draft_fix_node(self, state: AgentState) -> Dict:
        """Asks the LLM to write a code patch."""
        logger.info("[Agent] Drafting Code Patch...")
        return {"proposed_code": "def fixed_function(): pass"}

    def apply_and_test_node(self, state: AgentState) -> Dict:
        """Executes the patch safely and checks the output."""
        logger.info("[Agent] Applying Fix and running tests...")
        
        # Simulate test passing after 1 try
        if state["attempts"] > 1:
             return {"resolved": True, "test_results": "OK"}
             
        return {"resolved": False, "test_results": "Failed: SyntaxError"}

    def check_resolution_status(self, state: AgentState) -> str:
        """Determines if the graph should loop back or finish."""
        if state.get("resolved", False):
            logger.info("[Agent] Error successfully healed!")
            return "success"
            
        if state.get("attempts", 0) >= 3:
            logger.error("[Agent] Max attempts reached. Abandoning fix.")
            return "failed"
            
        logger.warning("[Agent] Fix failed. Retrying cycle...")
        return "retry"

    # ── Entrypoint ───────────────────────────

    def run_healing_cycle(self, error_message: str):
        """Starts the autonomous LangGraph application."""
        initial_state = {
            "error_message": error_message,
            "target_file": "unknown",
            "proposed_code": "",
            "test_results": "",
            "attempts": 0,
            "resolved": False
        }
        
        logger.info("Initializing Autonomous Self-Healing Graph...")
        final_state = self.graph.invoke(initial_state)
        return final_state
