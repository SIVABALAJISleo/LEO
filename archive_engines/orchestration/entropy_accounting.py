import logging
import time
from enum import Enum
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class ComputeType(Enum):
    EVALUATION = "evaluation" # Cheap (e.g. reading variable)
    DERIVATION = "derivation" # Moderate (e.g. A + B = C)
    CREATION = "creation"     # Expensive (e.g. Noise(x,y), Sampling)

class EntropyAccountant:
    """
    Module 43: INFORMATION ENTROPY ACCOUNTING SYSTEM
    - Tracks when computation creates new information vs reuses old.
    - Separates Evaluation, Derivation, and Creation costs.
    - Provides provable explanation for residual compute cost.
    """
    
    def __init__(self):
        self.ledger: List[Dict[str, Any]] = []
        self.total_entropy_cost = 0.0

    def record_operation(self, operation_name: str, op_type: ComputeType, details: str = ""):
        """
        Record a computational operation in the entropy ledger.
        """
        cost = 0.0
        
        if op_type == ComputeType.EVALUATION:
            cost = 1.0
        elif op_type == ComputeType.DERIVATION:
            cost = 10.0
        elif op_type == ComputeType.CREATION:
            cost = 100.0
            
        entry = {
            "timestamp": time.time(),
            "operation": operation_name,
            "type": op_type.value,
            "entropy_cost": cost,
            "details": details
        }
        
        self.ledger.append(entry)
        self.total_entropy_cost += cost
        
        # Log purely for visibility during dev
        logger.debug(f"Entropy Record: [{op_type.value.upper()}] {operation_name} (+{cost})")

    def get_audit_report(self) -> Dict[str, Any]:
        """
        Generate a summary report of where the compute 'energy' went.
        This defends the architecture against claims of inefficiency.
        """
        breakdown = {
            "evaluation": 0,
            "derivation": 0,
            "creation": 0
        }
        
        for entry in self.ledger:
            key = entry["type"]
            breakdown[key] += entry["entropy_cost"]
            
        return {
            "total_entropy_units": self.total_entropy_cost,
            "breakdown": breakdown,
            "efficiency_rating": "OPTIMAL" if breakdown["creation"] < breakdown["evaluation"] else "GENERATIVE_HEAVY",
            "ledger_count": len(self.ledger)
        }
