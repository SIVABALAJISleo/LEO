# Security Policy

## ONNX Supply-Chain Advisory (CVE-2026-28500 / Dependabot #54)

**Vulnerability**: onnx.hub.load() with silent=True suppresses
trust warnings allowing silent model download from untrusted repos.

**Our mitigation**:
1. onnx.hub.load() is NEVER called anywhere in this codebase
2. All model loading uses onnxruntime.InferenceSession(local_path)
3. patch_onnx_security() in backend/core/security.py enforces this
4. CI grep check blocks any future addition of hub.load() calls

**Why we do not upgrade onnx**:
No patched version exists. The onnx team removed the feature
in the next major version. Our non-usage is the correct mitigation.

**Status**: Mitigated by architectural choice. Alert dismissed as
"Vulnerable code is not actually called".
