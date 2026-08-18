# Security Policy & Governance

## Reporting Security Issues

**DO NOT** open public GitHub issues for security vulnerabilities.

Please report security issues directly to the security team:
- **Email**: `security@leo.ai`

### Vulnerability Disclosure Timeline
- **Discovery → Acknowledgment**: Within 24 hours
- **Triage & Initial Response**: Within 48 hours
- **Fix Release**: Critical (7 days), High/Medium (30 days)

---

## Supply-Chain & Architectural Advisories

### ONNX Advisory (CVE-2026-28500 / Dependabot #54)
- **Vulnerability**: `onnx.hub.load()` with `silent=True` suppresses trust warnings.
- **Our mitigation**:
  1. `onnx.hub.load()` is strictly forbidden and never called anywhere in the codebase.
  2. All model execution loads directly via `onnxruntime.InferenceSession(local_path)`.
  3. `patch_onnx_security()` in `backend/core/security.py` enforces local-only invocation.
  4. CI grep check blocks any future addition of `hub.load()` calls.
- **Status**: Fully mitigated by architecture.

---

## Security Best Practices

### Authentication & Secrets
- Never commit `.env`, `.pem`, `.key`, or service account JSON files.
- Passwords must be hashed using `bcrypt` (or Argon2) with salt rounds ≥ 12.
- JWT tokens use short-lived expiration (15 minutes) with rotating refresh tokens.

### API & Network Security
- All production traffic requires HTTPS.
- CORS restricted to whitelisted domains in production.
- Rate limiting and request payload limits enforced on ingress.
- Parameterized SQL queries via SQLAlchemy `text()` to prevent SQL injection.

### Frontend Security
- User-supplied HTML sanitized via `DOMPurify` (`src/utils/sanitize.ts`).
- Content Security Policy (CSP) headers applied via `SecurityHeadersMiddleware`.
