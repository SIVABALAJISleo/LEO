import sys
import os

# Allow running from project root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from hyper_runtime.entropy_governance.entropy_governor import LEOEntropyGovernor, InfrastructureBudgetViolation, RuleContractViolation
from hyper_runtime.entropy_governance.observability_tracer import LEOTracer

def run_benchmark():
    print("=" * 70)
    print("  LEO RUNTIME — PHASE 5: ENTROPY GOVERNANCE & OBSERVABILITY")
    print("=" * 70)
    
    governor = LEOEntropyGovernor()
    tracer = LEOTracer()
    
    query = "Reconcile corporate invoices against the Q3 tax ledger."
    trace_id = tracer.start_span(query)
    
    # 1. Successful execution that respects the constraints
    print("\n[1] Executing step respecting governance rules...")
    cost = {"estimated_flops": 1.2e9}
    contract = ["reconciled_invoice_dataset"]
    
    try:
        # Check constraints
        governor.assert_execution_preconditions(cost, contract)
        
        # Log to tracer
        tracer.log_routing_event(trace_id, "Invoice Reconciliation", {"status": "SUCCESS", "cost_spent_flops": 1.2e9})
        print("  Step completed successfully!")
    except Exception as e:
        print(f"  [!] Governance Blocked Execution: {e}")
        
    # 2. Violation of Rule 1 (Cost Declaration)
    print("\n[2] Attempting execution WITHOUT declaring cost...")
    try:
        governor.assert_execution_preconditions({}, contract)
    except RuleContractViolation as e:
        print(f"  [!] Governance Blocked Execution: {e}")
        tracer.log_routing_event(trace_id, "Failed Step", {"status": "BLOCKED", "reason": str(e)})
        
    # 3. Violation of Dependency Budget (Max 4 dependencies)
    print("\n[3] Simulating developers attempting to add a 5th dependency (e.g., PostgreSQL)...")
    try:
        governor.add_dependency("PostgreSQL")
    except InfrastructureBudgetViolation as e:
        print(f"  [!] Infrastructure Budget Blocked: {e}")
        
    # 4. View Trace Audit Trail
    print("\n[4] Inspecting Observability Audit Trail for trace:")
    for event in tracer.get_audit_trail(trace_id):
        print(f"  - Step: {event['step']:<25} | Details: {event['details']}")
        
    print("\n" + "=" * 70)
    print("  PHASE 5 SUMMARY")
    print("=" * 70)
    print("Entropy Governance enforces absolute limits on cost declarations, output")
    print("contracts, and dependency budgets. The Observability tracer guarantees")
    print("complete auditable, replayable narratives for every single routing action.")

if __name__ == "__main__":
    run_benchmark()
