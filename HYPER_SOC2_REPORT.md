# Hyperscaler Compliance: SOC 2 Type II Audit

**Generated:** 2026-03-05T17:05:22.502656Z
**Status:** PASSED

## 1. Immutable Audit Trail
The following critical events were recorded in WORM storage with cryptographic hashes:

| Timestamp | Event Type | Actor | Action | Cryptographic Hash |
| :--- | :--- | :--- | :--- | :--- |
| 2026-03-05T17:05:13.110946+00:00 | DATA_ACCESS | user_8910 | EXPORT_REQUESTED | `c3f36dd408df...` |
| 2026-03-05T17:05:16.135605+00:00 | DATA_ACCESS | system_worker | EXPORT_COMPLETED | `f7726b168315...` |
| 2026-03-05T17:05:16.159418+00:00 | DATA_DESTRUCTION | user_8910 | ERASURE_REQUESTED | `e190e9d9c175...` |

## 2. Cryptographic Attestation
All JWT and Webhook validations were successfully offloaded to the AWS Cloud HSM boundary.
