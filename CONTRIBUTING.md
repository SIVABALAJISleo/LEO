# Contributing to LEO AI

Thank you for your interest in contributing to LEO AI! This is a research project pushing the boundaries of software-only AI optimization.

---

## 🏗 Project Architecture

LEO AI is structured as a full-stack intelligence platform:

```text
HYPER/
├── backend/          # FastAPI Python backend
│   ├── core/         # Database, health, base configs
│   ├── routers/      # REST API endpoints
│   ├── security/     # Middleware (rate limiting, CSP, auth)
│   ├── memory/       # Knowledge graph and semantic cache
│   └── models/       # Pydantic data models
├── src/              # React frontend
├── supabase/         # Auth + DB config
├── nginx.conf        # Production HTTPS proxy
├── PRIVACY.md        # GDPR / DPDP compliance
├── TERMS.md          # Terms of Service
└── DISCLAIMER.md     # AI system disclaimer
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- Git

### Local Setup

```bash
# Clone the repository
git clone https://github.com/SIVABALAJISleo/LEO.git
cd LEO

# Backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn backend.main:app --reload

# Frontend
npm install
npm run dev
```

---

## 🤝 How to Contribute

1. **Fork** the repository
2. **Create a feature branch**: `git checkout -b feature/my-optimization`
3. **Make your changes** following the guidelines below
4. **Test your changes** — see Testing section
5. **Submit a Pull Request** with a clear description

---

## 📋 Contribution Guidelines

### Code Style

- Python: Follow PEP 8 formatting
- JavaScript/TypeScript: Follow ESLint config in the project
- All new API endpoints must include docstrings and type hints
- Security-sensitive code must include a comment explaining the security model

### Commit Messages

Use conventional commits:

```text
feat: add speculative decoding engine
fix: resolve memory leak in resonance cache
perf: optimize AVX2 kernel for BitNet
docs: update API documentation
security: patch CORS misconfiguration
```

### Testing Requirements

- All new backend endpoints must include unit tests in `backend/tests/`
- All new frontend components must include integration tests
- Performance benchmarks should not regress from baseline

---

## 🔒 Security Vulnerabilities

**Do NOT open a public GitHub issue for security vulnerabilities.**

Instead, please report them privately by opening a **confidential issue** on GitHub or by contacting the maintainer directly through the repository.

---

## 📦 Adding New AI Models

If you're integrating a new model:

1. Create a `models/<model-name>/NOTICE.md` with license terms — see `kimi-k3/NOTICE.md` as a template
2. Add any license restrictions to `README.md` (Third-Party Model License Notice section)
3. Ensure the model weights are NOT committed to the repository — use GitHub Releases for hosting

---

## 📜 License

By contributing, you agree that your contributions will be licensed under the MIT License that covers this project.

Third-party models integrated into LEO AI retain their original licenses. See `kimi-k3/NOTICE.md` for an example.
