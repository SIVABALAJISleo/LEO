# HYPER: Strategy Engine & Optimization Search

## 1. Strategy Representation
A strategy in HYPER represents a complete, reproducible configuration across eight orthogonal dimensions:
$$\text{Strategy} = \langle \text{Algorithm}, \text{Representation}, \text{Precision}, \text{TileSize}, \text{VectorWidth}, \text{DevicePartition}, \text{MemoryLayout}, \text{VerificationPolicy} \rangle$$

---

## 2. Multi-Objective Optimization
Instead of single-metric latency minimization, candidate strategies are evaluated across a multi-objective cost vector:
$$\mathbf{J} = \big[ \text{Latency}, \; W_{\text{total}}, \; \text{MemoryTraffic}, \; \text{RelativeError}, \; \text{VerificationCost} \big]$$

The search engine maintains a non-dominated Pareto set. A candidate $A$ dominates candidate $B$ ($A \prec B$) if and only if $A$ is no worse than $B$ across all objectives and strictly better in at least one objective.

---

## 3. Persistent Strategy Memory
Strategies that achieve Pareto optimality and pass all contract verifications are persisted to `HYPER_3_0_STRATEGY_DATABASE.json`. On recurring executions with matching workload fingerprints, the optimal historical strategy is retrieved in $O(1)$ time, eliminating recurring autotuning overhead.
