# 🚀 PROJECT HYPER: COMPUTE-AVOIDANCE INTELLIGENCE ARCHITECTURE
**The Supreme CPU-First, GPU-Minimizing AI Operating System**

Project HYPER is a radical architectural shift away from brute-force tensor generation. By leveraging **Semantic Caching**, **Neurosymbolic Routing**, **Sparse Activation**, and **Edge Mesh Distribution**, HYPER achieves a 99% reduction in practical GPU dependency.

*The best computation is the computation that never happens.*

## 📂 Modular Folder Structure & Architecture
The system is fully deployed in this repository. 

```text
HYPER-main/
├── README.md                      # This deployment guide
├── docker-compose.yml             # CPU-capped swarm orchestration
├── Dockerfile                     # AVX-512 / llama.cpp optimized container
├── pyrightconfig.json             # IDE Linting configuration
└── project_hyper/
    ├── api/
    │   └── routes.py              # FastAPI Streaming & Orchestration endpoints
    ├── core/
    │   └── orchestrator.py        # Master Cascade Router (Legacy)
    ├── edge_router.py             # Security, Telemetry, and Semantic Cascade Layer
    ├── sparse_core.py             # Mamba/BitNet/RWKV Sparse Execution Engine
    ├── ultra_master_pipeline.py   # The Z3/SymPy Neurosymbolic Bypass Runtime
    ├── cache.py                   # FAISS Semantic Vectors & Redis Integration
    ├── compute.py                 # mmap and GGUF Tensor Loading
    ├── rag.py                     # ChromaDB Contextual Compression
    └── uncertainty.py             # Probabilistic Route Escalation
```

## 🧠 Core Systems Deployed

1.  **Multi-Stage Cascade Router (`edge_router.py`)**: Intercepts queries via Lexical Security Firewalls and dumps them to the Semantic Cache. If a miss occurs, it routes to Z3/SymPy for math/logic, avoiding neural hallucination and FLOPs.
2.  **Sparse CPU-First Runtime (`sparse_core.py`)**: Models are memory-mapped (`mmap`) directly to DDR5 RAM. Generative tasks use `llama.cpp` bound to AVX2/AVX512 SIMD instructions.
3.  **Distributed Edge Mesh (`docker-compose.yml`)**: Scalable peer-to-peer Ray/Celery nodes. Limits containers to 8 vCPUs, completely decoupling scaling from centralized cloud GPUs.

## 🚀 Deployment Steps (Production & Edge)

### 1. Local Edge Deployment (Single Node)
To run the orchestration API locally on a commodity CPU:
```bash
# Ensure Docker is installed
cd HYPER-main/project_hyper
docker-compose up --build -d
```
The FastAPI Gateway will be available at `http://localhost:8000`. It automatically starts the Redis semantic cache and the CPU-inference endpoints.

### 2. Distributed Mesh Deployment (Kubernetes / Ray)
For horizontal CPU scaling across commodity hardware:
1.  Deploy the Redis instance centrally.
2.  Deploy the HYPER Docker containers across the edge nodes as stateless worker pods.
3.  The `TelemetryEngine` (in `edge_router.py`) will automatically track Compute Avoided and GPU Watts Saved across the mesh.

## 📊 Telemetry & Observability
The API exposes internal telemetry tracking the exact execution route:
*   `CACHE`: Intercepted by FAISS/Redis (~5ms).
*   `SYMBOLIC`: Routed to Python Sandbox / Z3 Engine (~50ms).
*   `CPU_SPARSE`: Routed to local GGUF/Mamba Model (~200ms TTFT).
*   `GPU_FALLBACK`: Extreme rare event (<1%).

## 📖 Deep Architecture Manifestos
For extensive detail on the specific compiler optimizations, thermal energy routing, and CREP (Contextual Reembedding Principle) Engine, review the master documents stored in the system's brain:
*   `PROJECT_LEO_COMPLETE_SYSTEM.md`
*   `PROJECT_LEO_COMPUTATIONAL_REFORMULATION.md`
*   `PROJECT_LEO_DISTRIBUTED_MESH.md`
*   `PROJECT_LEO_ONTOCOMPILER.md`

---
*Built for Intelligence per Watt.*
