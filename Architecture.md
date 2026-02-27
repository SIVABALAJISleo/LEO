# CPU-First Architecture Design

## 1. RAG Layer
Uses `faiss-cpu` for vector search and `sentence-transformers` for embeddings. This ensures low-latency retrieval without requiring VRAM.

## 2. Local Inference
Utilizes `llama-cpp-python` to execute GGUF-quantized models. These models are highly optimized for CPU instructions (AVX2, AVX512) and iGPU sharing.

## 3. Local-First UI
Data is persisted to `IndexedDB` via Dexie. Sync logic handles eventual consistency with the server, allowing the UI to remain responsive even under high network latency or offline conditions.

## 4. Probabilistic Structures
Uses Bloom Filters and HyperLogLog to perform approximate counting and set membership checks with minimal memory footprint, avoiding heavy database scans.
