import logging
from typing import Dict, Any, List

logger = logging.getLogger("HyperCore.EntropyGovernor")

class InfrastructureBudgetViolation(Exception):
    pass

class RuleContractViolation(Exception):
    pass

class LEOEntropyGovernor:
    """
    HyperCore PHASE 5 — Entropy Governance
    
    Enforces structural, application-level complexity boundaries.
    Asserts absolute constraints:
    1. Every computation must declare its latency/FLOP cost before execution.
    2. Every computation must declare a formal output contract.
    3. Maximum 4 external infrastructure dependencies (e.g., Kafka, Redis, OTel, Envoy).
    """
    def __init__(self):
        # Strict dependency tracking
        self.dependencies: List[str] = ["Kafka", "Redis", "OpenTelemetry", "Envoy"]
        
    def add_dependency(self, name: str):
        """Prevents uncontrolled dependency drift."""
        if len(self.dependencies) >= 4:
            raise InfrastructureBudgetViolation(
                f"Infrastructure Dependency Budget EXCEEDED! Maximum is 4. Cannot register '{name}'."
            )
        self.dependencies.append(name)
        
    def assert_execution_preconditions(self, declared_cost: Dict[str, Any], declared_contract: List[str]):
        """
        Enforces Rule 1 (Cost Declaration) and Rule 2 (Contract Declaration).
        """
        if not declared_cost or "estimated_flops" not in declared_cost:
            raise RuleContractViolation("Rule 1 VIOLATION: Execution blocked! Computation did not declare cost parameters.")
            
        if not declared_contract or len(declared_contract) == 0:
            raise RuleContractViolation("Rule 2 VIOLATION: Execution blocked! Computation lacks a declared output contract.")
            
        logger.info("Governance Preconditions SATISFIED. Cost and contract verified.")
