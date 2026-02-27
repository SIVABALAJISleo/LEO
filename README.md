# Project HYPER: Production-Grade Upgrade

## Safety & Scope
This project has been upgraded to a production-grade, CPU/iGPU-first architecture. It is designed to survive infrastructure failures and provide verifiable evidence of its operational state.

### Design Principles:
1. **CPU-First**: No GPU dependencies for core inference or processing.
2. **Local-First**: Offline-capable with optimistic UI and background sync.
3. **Audit-Ready**: Structured logging and automated test evidence generation.
4. **Resilient**: Circuit breakers, chaos testing, and automated rollbacks.

## Performance
- **RAG**: Optimized FAISS index for document retrieval.
- **Inference**: Small quantized GGUF models via `llama.cpp`.
- **Media**: Proxy workflow for background media processing.
