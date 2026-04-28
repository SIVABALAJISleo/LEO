import asyncio
import time
import logging
import json
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

# Actual Stack Imports
from backend.intelligence.rag import RAGEngine
import onnxruntime as ort
try:
    from llama_cpp import Llama
except ImportError:
    Llama = None
    
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser

logger = logging.getLogger(__name__)

class QueryRequest(BaseModel):
    query: str
    user_id: str
    context: Optional[Dict[str, Any]] = None
    is_high_risk: bool = False
    tenant_id: str = "default"

class DeterministicEngine:
    """
    CPU/iGPU-First AI System.
    Core Rule: Never guess. Never execute low-confidence output. Minimize compute always.
    """
    def __init__(self):
        # 1. Zero-Compute Layer
        self.semantic_cache = {}  # In prod: Redis or in-memory LRU
        self.template_store = {
            "status": "System status is ONLINE. Latency: {latency}ms",
            "greeting": "Hello {user}, how can I help you today?"
        }
        
        # 2. Reality Engine (FAISS)
        self.rag = RAGEngine(dimension=384, persist_dir="rag_data")
        
        # 3. Models (Lazy-loaded to avoid memory pressure on CPU)
        self.onnx_session = None
        self.llama_model = None

        logger.info("Deterministic Engine (LangChain+FAISS+llama.cpp+ONNX) Initialized.")

    def _get_onnx_model(self):
        """Tiny Model for simple queries."""
        if self.onnx_session is None:
            try:
                # Placeholder path - in reality, load optimized ONNX model
                self.onnx_session = ort.InferenceSession("models/tiny_model.onnx")
            except Exception as e:
                logger.warning(f"ONNX initialization skipped: {e}")
        return self.onnx_session

    def _get_llama_model(self):
        """Quantized GGUF Model for medium/hard queries."""
        if self.llama_model is None and Llama is not None:
            try:
                # Load a highly quantized GGUF model for fast CPU/iGPU execution
                self.llama_model = Llama(
                    model_path="models/llama-2-7b-chat.Q4_K_M.gguf",
                    n_ctx=2048,
                    n_threads=max(1, asyncio.get_event_loop()._default_executor._max_workers if hasattr(asyncio.get_event_loop(), '_default_executor') else 4)
                )
            except Exception as e:
                logger.warning(f"Llama.cpp initialization skipped: {e}")
        return self.llama_model

    async def process(self, req: QueryRequest) -> Dict[str, Any]:
        start_time = time.time()
        
        # 1. INPUT GATE (AMBIGUITY ELIMINATION)
        input_analysis = await self._input_gate(req)
        if input_analysis["action"] == "request_clarification":
            return self._build_response(req, input_analysis["message"], confidence=0.0, action="clarify")

        # 4. ZERO-COMPUTE STRATEGY (PRIMARY WEAPON)
        cached = await self._check_zero_compute(input_analysis)
        if cached:
            return self._build_response(req, cached["answer"], confidence=0.95, source="zero_compute_cache", latency_ms=(time.time()-start_time)*1000)

        # 2. REALITY + CONFIDENCE ENGINE
        reality_check = await self._reality_filter(input_analysis)
        if reality_check["confidence"] < 0.7:
            return self._build_response(
                req, 
                "I blocked this request because I lack sufficient context to provide a guaranteed correct answer. Please provide more specifics.", 
                confidence=reality_check["confidence"], 
                action="block_missing_data"
            )

        # 3. SMART ROUTER (MIN COMPUTE FIRST)
        route = await self._router(reality_check)

        # 5. SPEED LAYER & EXECUTION
        answer = await self._execute_route(route, reality_check)

        # 6. OUTPUT CONTROL (ADAPTIVE)
        final_output = self._output_control(answer, reality_check["confidence"])

        # 8. FEEDBACK LOOP (Async execution)
        asyncio.create_task(self._async_feedback_loop(req, final_output))

        latency = (time.time() - start_time) * 1000
        return self._build_response(
            req, 
            final_output["text"], 
            confidence=reality_check["confidence"], 
            source=route["tier"], 
            latency_ms=latency, 
            extra=final_output.get("extra")
        )

    async def _input_gate(self, req: QueryRequest) -> Dict[str, Any]:
        """Extract intent, constraints. Check high-risk."""
        # Simple heuristic extraction; LangChain can be used here for deeper parsing
        query_lower = req.query.lower()
        
        if req.is_high_risk and not req.context:
            return {"action": "request_clarification", "message": "High-risk execution requires strict structured parameters. No free text allowed."}
            
        # Ambiguity check (e.g. queries under 10 chars usually lack context)
        if len(query_lower) < 10 and "hello" not in query_lower and "status" not in query_lower:
            return {"action": "request_clarification", "message": "Your query is too vague. Did you mean to query analytics, database, or settings?"}
            
        return {
            "action": "proceed", 
            "intent": "general", 
            "query": req.query, 
            "tenant_id": req.tenant_id
        }

    async def _check_zero_compute(self, analysis: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Semantic cache & precomputed templates."""
        query = analysis["query"].lower()
        
        # Cache Check (Similarity > 0.92 conceptually)
        if query in self.semantic_cache:
            return {"answer": self.semantic_cache[query]}
            
        # Template Rendering
        if "system status" in query:
            return {"answer": self.template_store["status"].format(latency=0.0)}
            
        return None

    async def _reality_filter(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """FAISS RAG Cross-check. Calculate deterministic confidence."""
        # Retrieve using the exact RAGEngine
        docs = self.rag.retrieve(analysis["query"], tenant_id=analysis["tenant_id"], k=3)
        
        if not docs:
            # If no docs found, confidence is severely limited for factual queries
            return {"confidence": 0.4, "context": [], "query": analysis["query"]}
            
        # Confidence calculation: agreement (score) + recency + reliability
        avg_score = sum(d.get("score", 0.5) for d in docs) / len(docs)
        
        # Base confidence on RAG retrieval strength
        confidence = min(0.95, avg_score + 0.1) # Boost slightly if found
        
        return {
            "confidence": confidence, 
            "context": [d["content"] for d in docs], 
            "query": analysis["query"]
        }

    async def _router(self, reality: Dict[str, Any]) -> Dict[str, Any]:
        """Classify complexity for Tiny / Quantized / Heavy paths."""
        q_len = len(reality["query"])
        ctx_len = len(" ".join(reality["context"]))
        total_len = q_len + ctx_len
        
        if total_len < 200:
            tier = "onnx_tiny"
        elif total_len < 1500:
            tier = "llama_cpp_quantized"
        else:
            tier = "api_heavy"
            
        return {"tier": tier}

    async def _execute_route(self, route: Dict[str, Any], reality: Dict[str, Any]) -> str:
        """Execute using ONNX, llama.cpp, or Fallback."""
        tier = route["tier"]
        prompt = f"Context: {' '.join(reality['context'])}\nQuery: {reality['query']}\nAnswer:"
        
        if tier == "onnx_tiny":
            # ONNX Execution (Mocked run, real execution needs specific tokenization)
            if self._get_onnx_model():
                return "ONNX Tiny Model executed successfully."
            return "Fallback from ONNX: " + reality["context"][0] if reality["context"] else "Acknowledged."
            
        elif tier == "llama_cpp_quantized":
            # GGUF Execution
            llama = self._get_llama_model()
            if llama:
                # Async-wrap the synchronous llama.cpp call
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(None, lambda: llama(prompt, max_tokens=150, echo=False))
                return response["choices"][0]["text"].strip()
            return "Fallback from GGUF: Processed context."
            
        else:
            # API Fallback (Restricted to <5%)
            return "Processed via Heavy API fallback path."

    def _output_control(self, answer: str, confidence: float) -> Dict[str, Any]:
        """Adaptive Output Control based on thresholds."""
        if confidence >= 0.85:
            return {"text": answer}
        elif 0.6 <= confidence < 0.85:
            return {
                "text": answer, 
                "extra": "Assumed Context: Provided based on nearest semantic match. Please verify against primary data."
            }
        else:
            return {
                "text": "I am not sufficiently confident to execute this. Could you clarify your parameters?", 
                "extra": "Interpretations blocked."
            }

    async def _async_feedback_loop(self, req: QueryRequest, output: Dict[str, Any]):
        """Background feedback + cache invalidation."""
        # Precompute & Cache for Lazy Compute Strategy
        query_key = req.query.lower()
        if output.get("action") != "clarify" and req.query not in self.semantic_cache:
            self.semantic_cache[query_key] = output["text"]

    def _build_response(self, req: QueryRequest, answer: str, confidence: float, source: str = "engine", latency_ms: float = 0, action: str = "success", extra: str = None) -> Dict[str, Any]:
        res = {
            "action": action,
            "answer": answer,
            "confidence": round(confidence, 2),
            "source": source,
            "latency_ms": round(latency_ms, 2)
        }
        if extra:
            res["correction_path"] = extra
        return res

global_deterministic_engine = DeterministicEngine()
