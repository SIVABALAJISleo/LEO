# LEO x HYPER — Self-Improving Edge AI Engine

> *"The best inference is the one that never happens."*

**LEO (Local Edge Orchestrator)** is a memory-efficient, self-improving AI backend engineered for consumer laptop hardware. It eliminates cloud dependency while continuously learning from its own query patterns through the integrated **Claude Reflect System**.

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104%2B-green)](https://fastapi.tiangolo.com)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux-lightgrey)](DEPLOYMENT.md)

---

## What LEO Does

LEO intercepts every query before it reaches a heavy LLM. Through a cascade of semantic matching, cache lookup, and lightweight local inference, over **87% of queries are resolved in under 5ms** — without loading any large model.

```
User Query
    |
    v
[1] Semantic Cache Lookup  --hit--> Response (< 5ms)
    | miss
    v
[2] Fast Embedder Match    --hit--> Response (< 15ms)
    | miss
    v
[3] LEO Engine (local LLM) -------> Response (~500ms)
    |
    v
[4] Reflect System records trace -> auto-promotes to cache
```

---

## Architecture

### Core Stack

| Layer | Component | Purpose |
|-------|-----------|---------|
| **Engine** | `leo_engine.py` | Memory-efficient singleton, on-demand model lifecycle |
| **Cache** | `leo_cache.json` | Zero-latency semantic lookup store |
| **Reflect** | `backend/reflect/` | Self-improvement via Claude Reflect System |
| **API** | `backend/server.py` | FastAPI REST + `/v1/chat/completions` |
| **Frontend** | `src/` | React + TanStack Router UI |

### LEO v7 Memory-Efficient Engine

Designed specifically for **Intel Core i5-12450H / 16 GB RAM** constraints:

- **Serial model loading** — only one model in VRAM at a time
- **`gc.collect()` + `torch.cuda.empty_cache()`** after each model use
- **`FastSemanticEmbedder`** — zero-overhead TF-IDF fallback when SentenceTransformer unavailable
- **Persistent semantic cache** — survives restarts, grows over time

### Claude Reflect System Integration

LEO's reflection layer (`backend/reflect/leo_reflect_service.py`) continuously:

1. **Records every query trace** — source, latency, cache hit/miss, similarity score
2. **Extracts self-improvement signals** — identifies high-latency cache misses for promotion
3. **Auto-promotes patterns** — repeated LLM queries graduate to permanent 0ms cache entries
4. **Tracks productivity metrics** — compute time saved, hit rate trends, scaling health

**Live Reflect Metrics:**

```
Total Queries Analyzed:     16
Cache Hits:                 14  (87.5%)
Avg Latency:                86ms
Promoted Learnings:         5
Compute Time Saved:         ~21 seconds
Status:                     HEALTHY_SCALING
```

---

## Quick Start

### 1. Backend Server

```bash
cd backend
pip install -r ../requirements.txt
uvicorn server:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Frontend Dev Server

```bash
npm install
npm run dev
```

### 3. Verify Reflect System

```bash
python backend/reflect/leo_reflect_service.py
```

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/leo/orchestrate` | `POST` | Main query endpoint with cache + reflection |
| `/api/v1/leo/metrics` | `GET` | Live performance metrics |
| `/api/v1/leo/frontiers` | `GET` | Engine frontier status |
| `/api/v1/memory` | `GET/POST` | Persistent memory store |
| `/v1/chat/completions` | `POST` | OpenAI-compatible chat API |

---

## Hardware Requirements

| Spec | Minimum | Tested On |
|------|---------|-----------|
| CPU | Intel Core i5+ (8th gen+) | i5-12450H (P+E cores) |
| RAM | 8 GB | 16 GB DDR5 |
| GPU | iGPU / discrete | Intel UHD (Xe) |
| Storage | 20 GB free | NVMe SSD |
| OS | Windows 10+ / Linux | Windows 11 |

> **Note:** LEO is an experimental edge-optimized system for local-first AI. It does not compete with data-center hardware in raw throughput.

---

## Key Modules

| File | Role |
|------|------|
| `leo_engine.py` | Core inference engine (v7 memory-efficient) |
| `leo_v7_memory_efficient.py` | Standalone v7 edition |
| `populate_cache.py` | Seed the semantic cache with FAQ data |
| `backend/reflect/leo_reflect_service.py` | Reflection + learning ledger service |
| `test_reflect_integration.py` | Integration test suite |
| `backend/server.py` | FastAPI REST backend |

---

## Deployment

- **Vercel** (frontend) — see `vercel.json`
- **Railway / Docker** — see `Dockerfile.backend` and `railway.toml`
- **Local** — `uvicorn server:app` from `backend/`

Full deployment guide: [DEPLOYMENT.md](DEPLOYMENT.md)

---

## Documentation

| Document | Description |
|----------|-------------|
| [Architecture.md](Architecture.md) | Full 17-layer system design |
| [LEO_Whitepaper.md](LEO_Whitepaper.md) | Technical whitepaper |
| [PERFORMANCE_REPORT.md](PERFORMANCE_REPORT.md) | Benchmark results |
| [SECURITY.md](SECURITY.md) | Security hardening notes |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Contribution guide |
| [DEPLOYMENT.md](DEPLOYMENT.md) | Deployment instructions |
| [RELEASE_NOTES.md](RELEASE_NOTES.md) | Version history |

---

## Background: HYPER v5.0 Compute Modules

The 6 core algorithmic breakthrough modules powering LEO's efficient compute:

1. **Neural GEMM Surrogate** — O(K) feature sketch projection via `np.tile` block structures
2. **Compressed Sensing FFT** — Candes-Tao spectral reconstruction from partial measurements
3. **Tensor Train GEMM** — Oseledets low-rank decompositions for 99.7% element reduction
4. **Multi-Fidelity Renderer** — SSGI to Embree+OIDN 4 SPP upscaling
5. **Causal Invariant Physics** — O(N) Pearl causal invariant modeling
6. **AlphaTensor Shape-Specialization** — Minimal-multiplication tiled schedules for iGPU SIMD

---

## License

[MIT](LICENSE) — Built for local-first, privacy-preserving AI.

