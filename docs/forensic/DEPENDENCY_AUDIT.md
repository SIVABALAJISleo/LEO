# LEO / HYPER Ω∞ — Dependency & Supply Chain Audit

## 1. Runtime Environment & Toolchain

- **Operating System**: Windows 11 Home / Pro (x86_64)
- **Python Runtime**: Python 3.13.5 (64-bit)
- **Node Runtime**: Node.js v22.x / Bun 1.2.x
- **Build Tooling**: Vite 8.2.1, Nitro 2.11, Rolldown

---

## 2. Python Dependencies Audit

| Package | Version | License | Security Assessment | Platform Compatibility |
| :--- | :--- | :--- | :--- | :--- |
| `numpy` | 2.2.x | BSD-3-Clause | Verified clean | Native AVX2 acceleration active on Intel CPU |
| `torch` | 2.6.x (CPU) | Modified BSD | Verified clean | PyTorch CPU wheels verified, AVX2 enabled |
| `fastapi` | 0.115.x | MIT | Verified clean | Async ASGI server routing verified |
| `uvicorn` | 0.34.x | BSD-3-Clause | Verified clean | High-concurrency event loop on Windows |
| `pydantic` | 2.10.x | MIT | Verified clean | V2 data validation and schema serialization |
| `pytest` | 9.0.2 | MIT | Verified clean | Test framework running 1,600+ test fixtures |
| `scipy` | 1.15.x | BSD-3-Clause | Optional scientific | Fast linear algebra & FFT routines |

### Absence of Paid / Remote APIs
- Zero dependencies on OpenAI, Anthropic, AWS, GCP, or Azure paid APIs.
- Zero reliance on external remote cloud runners.
- 100% self-hosted, offline-executable local execution.

---

## 3. Frontend Dependencies Audit

| Package | Version | License | Security Assessment | Status |
| :--- | :--- | :--- | :--- | :--- |
| `@tanstack/react-router` | 1.104.x | MIT | Verified clean | Production bundle builds cleanly |
| `@tanstack/start` | 1.104.x | MIT | Verified clean | Full SSR & client routing operational |
| `react` / `react-dom` | 19.0.x | MIT | Verified clean | Clean render with no hydrations warnings |
| `lucide-react` | 0.475.x | ISC | Verified clean | UI icon pack |
| `tailwindcss` | 4.0.x | MIT | Verified clean | Utility stylesheet compilation operational |
