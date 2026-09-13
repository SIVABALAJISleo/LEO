# HYPER / LEO — Fail-Closed Verification Specification
**Document Version:** 2.0.0 (Ultra-Sonic Master Engineering)

---

## 1. Fail-Closed Verification Rules

The Authoritative Verifier operates under strict fail-closed constraints:

1. **Default State is UNKNOWN**:
   - In the absence of positive proof, the verification status remains `UNKNOWN`.
   - Any runtime exception or failure in reference evaluation yields `UNKNOWN` or `FAIL`.
   - Code is forbidden from setting `verification_status = True` without physical execution evidence.

2. **Candidate-Coupled Verification**:
   - The candidate that is benchmarked MUST be the candidate that is verified.
   - It is forbidden to benchmark candidate $A$ and verify baseline $B$.

3. **Conjunctive Numerical Criteria**:
   - For bounded numerical tasks, PASS requires:
     $$\text{abs\_error} \le \text{absolute\_tolerance} \quad \text{AND} \quad \text{rel\_error} \le \text{relative\_tolerance}$$
   - Disjunctive conditions ($\text{abs\_error} > \text{tol} \text{ AND } \text{rel\_error} > \text{tol}$) are explicitly prohibited as rejection criteria.

4. **Blind Holdout & Generalization Gap**:
   - Final evaluation must execute on blind unseen data.
   - Generalization gap $|\text{Error}_{\text{holdout}} - \text{Error}_{\text{train}}|$ must be measured and reported. Zero generalization gap is never hardcoded.
