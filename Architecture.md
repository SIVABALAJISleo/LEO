# CPU-First Architecture Design

## 1. RAG Layer
Uses `faiss-cpu` for vector search and `sentence-transformers` for embeddings. This ensures low-latency retrieval without requiring VRAM.

## 2. Local Inference
Utilizes `llama-cpp-python` to execute GGUF-quantized models. These models are highly optimized for CPU instructions (AVX2, AVX512) and iGPU sharing.

## 3. Local-First UI
Data is persisted to `IndexedDB` via Dexie. Sync logic handles eventual consistency with the server, allowing the UI to remain responsive even under high network latency or offline conditions.

## 4. Probabilistic Structures
Uses Bloom Filters and HyperLogLog to perform approximate counting and set membership checks with minimal memory footprint, avoiding heavy database scans.

## 5. Universal AI Orchestration
The system utilizes a multi-layered intent resolution pipeline:
- **Intent Triangulation**: Extracts three possible interpretations of every query.
- **Speculative Routing**: Simultaneously evaluates compute routes (CPU vs. Quantized Model).
- **Reality Grounding**: Cross-verifies AI outputs against the vector DB and symbolic kernels.

## 6. Reliability & Zero-Failure Principle
- **Bounded Uncertainty**: Every response includes a calibrated confidence score and explicit failure modes.
- **Instant Correction**: The system implements an asynchronous feedback loop that processes copy/edit/re-ask signals to refine future behavior.
- **No Silent Failures**: If confidence falls below 0.6, the system is mandated to ask for clarification rather than hallucinating.
