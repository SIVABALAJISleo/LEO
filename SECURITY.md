# Project HYPER - Security Posture

This document details the security measures and vulnerability remediations for Project HYPER.

## Vulnerability Remediation Status

| Dependency | Fixed Version | Status | Mitigation / Note |
|------------|---------------|--------|-------------------|
| `ujson`    | `5.12.0`      | ✅ Fixed | Patched memory leak and integer overflow (CVE-2026-32874, CVE-2026-32875). |
| `pypdf`    | `6.9.1`       | ✅ Fixed | Patched infinite loop / DoS vulnerability in stream decoding. |
| `onnx`     | `1.20.1`      | ✅ Safe  | Codebase **does not use** `onnx.hub.load()`. All models loaded locally. |

## Why the ONNX Alert is N/A
The GitHub Dependabot Alert #54 concerns a vulnerability suppressed by `silent=True` in `onnx.hub.load()`. 
**Project HYPER is not affected** because:
1.  We do not use `onnx.hub.load()`.
2.  We perform strictly **local inference** via `onnxruntime`.
3.  We have updated to `onnx==1.20.1` (latest available) to minimize risk.
4.  **Dependabot Alert #54** may persist until `onnx==1.21.0` is released in April 2026, but it is **false positive** for this project given our usage.

## Security Practices
- **Zero-Binary Strategy**: We avoid untrusted binary downloads during runtime.
- **Dependency Isolation**: All business logic is isolated from low-level model handling via the Orchestrator.
- **Audit Logging**: Production interactions are logged with immutable audit trails.

## Reporting a Vulnerability
If you discover a security issue, please maintain project integrity by reporting it privately via the repository's Security tab.
