# HYPER / LEO Safe Deprecation Plan

## 1. Deprecation Strategy
In accordance with Sections 3 and 54 of the Master Evolution Protocol:
- **No Working Code is Deleted**: Old prototypes, benchmark harnesses, and heuristic modules remain in the repository under their classified namespaces (`LEGACY`, `EXPERIMENTAL`, or `ARCHIVED`).
- **Isolation of Unsafe Modules**: Any module containing hardcoded pass values (`default=True`), mock latencies (`time.sleep`), or unverified shortcut claims is decoupled from the authoritative execution path.
- **Migration via Adapters**: Older modules that offer valid mathematical insights are wrapped with `ContractIR` adapters so their proposals can be checked by the fail-closed verifier.

---

## 2. Deprecation Schedule
| Component / Pattern | Current Classification | Deprecation Action | Replacement in vNext |
| :--- | :--- | :--- | :--- |
| Hardcoded 100% Scorecard in `strict/scorecard.py` | `UNSAFE_FOR_PARITY_CLAIMS` | Deprecate static numbers; replace with dynamic query | `hyper_x/dashboard.py` (queries `evidence_ledger.json`) |
| Unverified Speculative Drafts | `UNSAFE_FOR_PARITY_CLAIMS` | Relabel as `PREDICTIVE_APPROXIMATION` | `hyper_runtime/speculative_decoding/speculative_calibration.py` |
| Monolithic CLI Scripts | `LEGACY` | Wrap into `hyper_x.pipeline` | `hyper_x/cli.py` & `hyper_x/pipeline.py` |
| Static Benchmark Constants | `LEGACY` | Remove; enforce wall-clock measurement | `hyper_x/benchmark/harness.py` |
