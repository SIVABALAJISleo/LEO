# HYPER Computational Wormhole Discovery Methodology
**Framework**: Counterfactual-Guided Autonomous Algorithm Discovery & Equality Saturation.

---

## 1. Multi-Level Search Hierarchy

The discovery engine explores 13 hierarchical search levels, moving from low-cost algebraic transforms to deep structural syntheses:

```
 LEVEL 0: Exact Cache & Memoization
 LEVEL 1: Incremental & Delta Computation
 LEVEL 2: Dependency & Unobserved Operation Elimination
 LEVEL 3: Algebraic Reformulation (Associativity, Commutativity)
 LEVEL 4: Representation Transformation (Sparse, Low-Rank, Quantized)
 LEVEL 5: Structural Sparsity & Inactive Neuron/Expert Skipping
 LEVEL 6: Bilinear & Tensor Factorization
 LEVEL 7: E-Graph Rewrite & Equality Saturation
 LEVEL 8: Algorithm Synthesis & Grammar Composition
 LEVEL 9: Multi-Objective Evolutionary Search
 LEVEL 10: LLM-Guided Hypothesis Generation
 LEVEL 11: Heterogeneous CPU + Intel UHD Hybrid Co-Execution
 LEVEL 12: Completely Novel Hybrid Representation Synthesis
```

Search does not blindly default to higher levels. It evaluates the **Expected Value of Search (EVS)**:
$$\text{EVS} = P(\text{success}) \cdot \mathbb{E}[\text{Work Saved}] - \text{Cost}(\text{Search})$$
If compiling and exploring a Level 10 genetic search costs 10 minutes of CPU time to save $0.5$ ms in a single-shot batch, the engine prunes the search branch immediately.

---

## 2. Autonomous Research Loop

The discovery engine operates as a continuous, self-rectifying scientific loop:

```
                   ┌──────────────┐
                   │   OBSERVE    │  Profile intrinsic tensor traits (rank, sparsity, conditioning)
                   └──────┬───────┘
                          ▼
                   ┌──────────────┐
                   │ HYPOTHESIZE  │  Generate counterfactual transformation hypotheses
                   └──────┬───────┘
                          ▼
                   ┌──────────────┐
                   │   GENERATE   │  Synthesize candidate expressions via Algorithm Grammar
                   └──────┬───────┘
                          ▼
                   ┌──────────────┐
                   │   COMPILE    │  Construct G', partition across CPU AVX2 & Intel UHD
                   └──────┬───────┘
                          ▼
                   ┌──────────────┐
                   │   EXECUTE    │  Run candidate on real physical hardware
                   └──────┬───────┘
                          ▼
                   ┌──────────────┐
                   │    VERIFY    │  9-layer verifier stack (Exact, Frobenius, Freivalds)
                   └──────┬───────┘
                          ▼
                   ┌──────────────┐
                   │   FALSIFY    │  Adversarial stress generator attacks candidate
                   └──────┬───────┘
                          ▼
                   ┌──────────────┐
                   │    LEARN     │  Success → Discovery Certificate; Failure → Counterexample Record
                   └──────┬───────┘
                          │
                          └──────► RE-SEARCH WITH UPDATED KNOWLEDGE BASE
```

---

## 3. Role of LLMs in the Discovery Engine

When an LLM (local or cloud) is connected to the engine:
1. **Hypothesis Generation Only**: The LLM proposes candidate mathematical transformations, novel representations, and domain-inspired decomposition strategies.
2. **ZERO Authority Over Correctness**: An LLM is NEVER permitted to declare `PASS`, `VERIFIED`, or `CORRECT`.
3. **Formal Verification Gate**:
   $$\text{LLM Output} \longrightarrow \text{HYPOTHESIS}$$
   $$\text{Wormhole Compiler} \longrightarrow \text{CANDIDATE PROGRAM}$$
   $$\text{Multi-Verifier Stack} \longrightarrow \text{EMPIRICAL EVIDENCE}$$
   $$\text{Scientific Auditor} \longrightarrow \text{CERTIFIED CLAIM}$$

---

## 4. Counterexample-Guided Inductive Synthesis (CEGIS)

When an optimization fails during adversarial stress testing:
1. The failing input $(A_{\text{bad}}, B_{\text{bad}})$ and the mathematical invariant violated are packaged into a `CounterexampleRecord`.
2. The failure signature is indexed in `CandidateRegistry.failure_knowledge_base`.
3. Future synthesis iterations query the registry:
   `is_known_failure(grammar_expression, workload_traits) -> bool`
   If a proposed mutation matches a known failure pattern, it is pruned before execution, preventing cyclic failures.
