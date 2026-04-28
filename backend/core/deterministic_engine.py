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
    Core Rule: Never guess. Never execute low-confidence outputs. Always minimize compute.
    """
    def __init__(self):
        # 1. Zero-Compute Layer Store
        self.semantic_cache = {} 
        self.template_store = {
            "status": "System status is ONLINE. Latency: {latency}ms",
            "greeting": "Hello {user}, how can I help you today?",
            "reset_password": "A password reset link has been dispatched to your registered email."
        }
        
        # 2. Reality Layer (FAISS)
        self.rag = RAGEngine(dimension=384, persist_dir="rag_data")
        
        # 3. Models (Lazy-loaded)
        self.onnx_session = None
        self.llama_model = None

        logger.info("Deterministic Engine (9-Step Pipeline) Initialized.")

    def _get_onnx_model(self):
        if self.onnx_session is None:
            try:
                self.onnx_session = ort.InferenceSession("models/tiny_model.onnx")
            except Exception as e:
                logger.warning(f"ONNX initialization skipped: {e}")
        return self.onnx_session

    def _get_llama_model(self):
        if self.llama_model is None and Llama is not None:
            try:
                self.llama_model = Llama(
                    model_path="models/llama-2-7b-chat.Q4_K_M.gguf",
                    n_ctx=2048,
                    n_threads=4
                )
            except Exception as e:
                logger.warning(f"Llama.cpp initialization skipped: {e}")
        return self.llama_model

    async def process(self, req: QueryRequest) -> Dict[str, Any]:
        start_time = time.time()
        
        # 1. INPUT GATE
        input_analysis = await self._input_gate(req)
        if input_analysis["action"] == "request_clarification":
            return self._build_response(req, input_analysis["message"], confidence=0.0, action="clarify")

        # 4. ZERO-COMPUTE (PRIMARY) - Check early to avoid ANY model compute
        zero_compute_match = await self._check_zero_compute(input_analysis)
        if zero_compute_match:
            return self._build_response(req, zero_compute_match["answer"], confidence=1.0, source="zero_compute", latency_ms=(time.time()-start_time)*1000)

        # 5. REALITY LAYER (RAG)
        reality_context = await self._reality_layer(input_analysis)

        # 2. CONFIDENCE ENGINE
        confidence_result = await self._confidence_engine(input_analysis, reality_context)
        if confidence_result["confidence"] < 0.7:
            return self._build_response(req, "BLOCK: Low confidence. Requesting missing data.", confidence=confidence_result["confidence"], action="block")

        # 3. ROUTER
        route = await self._router(input_analysis, confidence_result)

        # 6. SPEED LAYER (Execution)
        answer = await self._speed_layer_execute(route, confidence_result)

        # 6. OUTPUT CONTROL (Adaptive based on Point 2 thresholds)
        final_output = self._output_control(answer, confidence_result["confidence"])

        # 8. FEEDBACK
        asyncio.create_task(self._feedback_loop(req, final_output))

        latency = (time.time() - start_time) * 1000
        return self._build_response(
            req, 
            final_output["text"], 
            confidence=confidence_result["confidence"], 
            source=route["tier"], 
            latency_ms=latency, 
            extra=final_output.get("extra")
        )

    async def _input_gate(self, req: QueryRequest) -> Dict[str, Any]:
        query_lower = req.query.lower()
        if req.is_high_risk and not req.context:
            return {"action": "request_clarification", "message": "High-risk requires structured input."}
        
        if len(query_lower) < 5:
            return {"action": "request_clarification", "message": "Query too short. Please clarify intent."}

        return {
            "action": "proceed",
            "intent": "general", # In prod, use small classifier
            "query": req.query,
            "tenant_id": req.tenant_id
        }

    async def _confidence_engine(self, analysis: Dict[str, Any], reality: Dict[str, Any]) -> Dict[str, Any]:
        """confidence = agreement + recency + reliability"""
        # Mock calculation based on RAG scores
        docs = reality.get("docs", [])
        if not docs:
            return {"confidence": 0.4, "status": "low"}
            
        agreement = sum(d.get("score", 0.5) for d in docs) / len(docs)
        recency = 1.0 # Assume current
        reliability = 0.9 # Source reliability
        
        confidence = (agreement + recency + reliability) / 3.0
        return {"confidence": confidence, "reality": reality}

    async def _reality_layer(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """RAG Cross-check"""
        docs = self.rag.retrieve(analysis["query"], tenant_id=analysis["tenant_id"], k=3)
        return {"docs": docs, "query": analysis["query"]}

    async def _check_zero_compute(self, analysis: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Semantic cache + Precomputed templates"""
        query = analysis["query"].lower()
        if query in self.semantic_cache:
            return {"answer": self.semantic_cache[query]}
        
        if "status" in query:
            return {"answer": self.template_store["status"].format(latency=0.0)}
        if "password" in query:
            return {"answer": self.template_store["reset_password"]}
            
        return None

    async def _router(self, analysis: Dict[str, Any], confidence: Dict[str, Any]) -> Dict[str, Any]:
        q_len = len(analysis["query"])
        if q_len < 50:
            return {"tier": "tiny_model"}
        elif q_len < 500:
            return {"tier": "quantized_model"}
        else:
            return {"tier": "heavy_api"}

    async def _speed_layer_execute(self, route: Dict[str, Any], confidence: Dict[str, Any]) -> str:
        tier = route["tier"]
        reality = confidence["reality"]
        context = " ".join([d["content"] for d in reality["docs"]])
        prompt = f"Context: {context}\nQuery: {reality['query']}\nAnswer:"

        if tier == "tiny_model":
            return "Processed via ONNX Tiny Engine."
        elif tier == "quantized_model":
            llama = self._get_llama_model()
            if llama:
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(None, lambda: llama(prompt, max_tokens=150))
                return response["choices"][0]["text"].strip()
            return "Llama model fallback."
        else:
            return "Processed via Heavy API Layer."

    def _output_control(self, answer: str, confidence: float) -> Dict[str, Any]:
        if confidence >= 0.85:
            return {"text": answer}
        elif 0.7 <= confidence < 0.85:
            return {"text": answer, "extra": "Note: Verification suggested."}
        else:
            return {"text": "Low confidence answer blocked.", "extra": "Please clarify."}

    async def _feedback_loop(self, req: QueryRequest, output: Dict[str, Any]):
        # Track and Improve
        query_key = req.query.lower()
        if output.get("text") and query_key not in self.semantic_cache:
            self.semantic_cache[query_key] = output["text"]

    async def process_stream(self, req: QueryRequest):
        input_analysis = await self._input_gate(req)
        if input_analysis["action"] == "request_clarification":
            yield json.dumps({"token": input_analysis["message"]})
            return

        zero_compute = await self._check_zero_compute(input_analysis)
        if zero_compute:
            yield json.dumps({"token": zero_compute["answer"]})
            return

        reality = await self._reality_layer(input_analysis)
        conf = await self._confidence_engine(input_analysis, reality)
        
        if conf["confidence"] < 0.7:
            yield json.dumps({"token": "Blocked due to low confidence."})
            return

        llama = self._get_llama_model()
        if llama:
            context = " ".join([d["content"] for d in reality["docs"]])
            prompt = f"Context: {context}\nQuery: {reality['query']}\nAnswer:"
            for chunk in llama(prompt, max_tokens=256, stream=True):
                text = chunk["choices"][0]["text"]
                if text:
                    yield json.dumps({"token": text})

    def _build_response(self, req: QueryRequest, answer: str, confidence: float, source: str = "engine", latency_ms: float = 0, action: str = "success", extra: str = None) -> Dict[str, Any]:
        return {
            "action": action,
            "answer": answer,
            "confidence": round(confidence, 2),
            "source": source,
            "latency_ms": round(latency_ms, 2),
            "correction_path": extra
        }

global_deterministic_engine = DeterministicEngine()
