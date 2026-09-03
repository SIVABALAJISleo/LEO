# HYPER Research Mode & CLI Specification

## 1. Overview
HYPER Research Mode allows developers and auditors to explore new workloads, synthesize novel algorithms, verify stability against adversarial attacks, and benchmark execution directly from the command line.

---

## 2. Universal CLI Commands

```bash
# Forensic repository audit & consistency verification
hyper audit

# Inspect a workload and analyze its information requirements
hyper analyze <workload_name>

# Execute full MVC-DAR optimization pipeline on a workload
hyper optimize <workload_name> --contract <contract.yaml>

# Autonomous AI algorithm synthesis and evolutionary search
hyper discover <workload_name> --generations 50 --population 20

# Run independent verification and adversarial falsification
hyper verify <workload_name> --metamorphic --adversarial

# Execute canonical 15-workload benchmark suite with Track A & Track B
hyper benchmark all --reps 10 --warmup 3

# Automated research hypothesis generation, compilation, and report
hyper research <workload_name>

# Explain step-by-step optimization decisions for a specific run
hyper explain <run_id>

# Profile local hardware (P/E cores, UHD Xe execution units, RAM bandwidth)
hyper hardware

# Inspect current Pareto frontier leaderboard
hyper leaderboard

# Test candidate strategy on the frozen blind holdout dataset
hyper holdout <workload_name>

# Roll back an experimental strategy to the last trusted baseline
hyper rollback <workload_name>
```
