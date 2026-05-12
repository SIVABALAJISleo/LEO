import asyncio
import time
from project_hyper.layers.l0_intelligence import QueryIntelligence
from project_hyper.layers.l1_exact_cache import ExactCache
from project_hyper.layers.l2_semantic_cache import SemanticCache
from project_hyper.layers.l3_template_engine import TemplateEngine
from project_hyper.layers.l4_rag_system import RAGSystem
from project_hyper.layers.l5_tool_router import ToolRouter
from project_hyper.layers.l6_cpu_engine import CPULLMEngine
from project_hyper.layers.l7_reasoning import AdvancedReasoning
from project_hyper.layers.l8_speculative_decoding import SpeculativeDecodingEngine
from project_hyper.layers.l9_reasoning_graph import PrecomputedReasoningGraph
from project_hyper.layers.l10_gpu_fallback import GPUFallback
from project_hyper.layers.l11_learning_loop import LearningLoop

class ProjectLEO:
    """
    PROJECT HYPER: ZERO-GPU Cascaded AI System (12 Layers)
    """
    def __init__(self):
        self.l0 = QueryIntelligence()
        self.l1 = ExactCache()
        self.l2 = SemanticCache()
        self.l3 = TemplateEngine()
        self.l4 = RAGSystem()
        self.l5 = ToolRouter()
        self.l6 = CPULLMEngine()
        self.l7 = AdvancedReasoning()
        self.l8 = SpeculativeDecodingEngine()
        self.l9 = PrecomputedReasoningGraph()
        self.l10 = GPUFallback()
        self.l11 = LearningLoop()

    async def solve(self, query: str) -> str:
        start_time = time.time()
        trace = []
        
        # L0: Intelligence
        analysis = self.l0.analyze(query)
        trace.append(f"L0:{analysis['classification']}")

        # L1: Exact Cache
        hit = self.l1.get(query)
        if hit:
            trace.append("L1:HIT")
            self._finalize(query, hit, trace, start_time)
            return hit

        # L2: Semantic Cache
        hit = self.l2.get(query)
        if hit:
            trace.append("L2:HIT")
            self._finalize(query, hit, trace, start_time)
            return hit

        # L3: Template Engine
        res = self.l3.match(query)
        if res:
            trace.append("L3:MATCH")
            self._finalize(query, res, trace, start_time)
            return res

        # L9: Precomputed Reasoning Graph (Check if we have an offline path)
        graph_path = self.l9.traverse(analysis.get('type', '').lower())
        if graph_path and analysis['classification'] != "COMPLEX":
            trace.append("L9:GRAPH_HIT")
            self._finalize(query, graph_path, trace, start_time)
            return graph_path

        # L5: Tool Router
        if analysis['classification'] == "TOOL":
            trace.append("L5:TOOL")
            res = self.l5.execute_tool(analysis['type'], {"expression": query})
            self._finalize(query, res, trace, start_time)
            return res

        # L4: RAG System
        context = self.l4.retrieve(query)
        trace.append("L4:CONTEXT")

        # LLM Routing (L6, L7, L8)
        res = None
        if analysis['classification'] == "COMPLEX":
            trace.append("L7:REASONING")
            # For complex tasks, use self-consistency over the CPU engine
            res = self.l7.self_consistency(query, lambda q: self.l6.generate(q, context=context))
        else:
            # Use L8 (Speculative Decoding) if configured, else standard L6
            trace.append("L8:SPECULATIVE_DECODING")
            res = self.l8.generate_with_speculation(query, self.l6)

        # L10: GPU Fallback (Rare)
        if not res or analysis['classification'] == "HARD_FALLBACK" or (analysis['entropy'] > 5.5 and analysis['classification'] == "COMPLEX"):
            trace.append("L10:GPU_API")
            res = await self.l10.generate_async(query)

        self._finalize(query, res, trace, start_time)
        return res

    def _finalize(self, query: str, response: str, trace: list, start_time: float):
        latency = time.time() - start_time
        trace_str = " -> ".join(trace)
        print(f"[HYPER] Latency: {latency:.4f}s | Trace: {trace_str}")
        self.l11.record(query, response, trace_str, latency)
        # Update caches
        self.l1.set(query, response)
        self.l2.add(query, response)

if __name__ == "__main__":
    async def main():
        leo = ProjectLEO()
        await leo.solve("Hi")
        await leo.solve("x^2 + 5 = 10")
        await leo.solve("troubleshoot_network")
        await leo.solve("Explain the concept of entropy in zero-gpu systems.")
        
    asyncio.run(main())
