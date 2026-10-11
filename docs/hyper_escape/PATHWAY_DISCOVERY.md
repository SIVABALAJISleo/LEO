# Alternative Algorithm Discovery Engine

## 1. Overview & Search Space

The **Alternative Algorithm Discovery Engine** (`hyper_universal/pathway_discovery/search.py`) explores a bounded combinatorial search space of algorithmic alternatives for any given workload contract.

### Candidate Structure
```python
@dataclass
class PathwayCandidate:
    candidate_id: str
    name: str
    algorithm_family: str
    transformation_kind: str
    kernel_fn: Callable[[Any], Any]
    precondition_check: Callable[[Any], bool]
    status: DiscoveryStatus
    measured_speedup: float
    max_relative_error: float
    rejection_reason: str
```

---

## 2. Discovery Search Procedure

1. **Baseline Evaluation:** Run and benchmark trusted canonical baseline; capture reference output and timing.
2. **Precondition Gating:** Evaluate static and dimension preconditions (e.g., matrix sparsity, dimension divisibility, dynamic range). Reject ineligible candidates without running them.
3. **Bounded Candidate Execution:** Execute eligible candidates under a strict wall-clock deadline (default 2000 ms).
4. **Differential Output Verification:** Validate candidate output strictly against reference under the declared contract.
5. **Performance Gating:** Candidates that introduce severe regressions (speedup $< 0.5\times$) are flagged with `REJECTED_PERFORMANCE_REGRESSION`.
6. **Winner Selection & Evidence Storage:** The fastest verified candidate is crowned `VERIFIED_WINNER` and committed to the persistent evidence store.
