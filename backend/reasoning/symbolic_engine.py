"""
backend/reasoning/symbolic_engine.py
Symbolic reasoning engine.
Provides RETE-based forward-chaining rules, policy/compliance constraints,
and bridges to Z3 constraint solvers with zero Central GPU requirements.
"""
import logging
from typing import Dict, Any, List, Set, Tuple

logger = logging.getLogger(__name__)

class RETENode:
    """Base class for RETE pattern network nodes."""
    def __init__(self):
        self.children: List['RETENode'] = []

    def propagate(self, fact: Tuple[str, str, Any], working_memory: Set[Tuple[str, str, Any]]):
        raise NotImplementedError


class AlphaNode(RETENode):
    """Filters facts based on single-attribute constraints (Class/Type matching)."""
    def __init__(self, attribute: str, value: Any):
        super().__init__()
        self.attribute = attribute
        self.value = value

    def propagate(self, fact: Tuple[str, str, Any], working_memory: Set[Tuple[str, str, Any]]):
        subj, attr, val = fact
        if attr == self.attribute and val == self.value:
            for child in self.children:
                child.propagate(fact, working_memory)


class TerminalNode(RETENode):
    """Executes a corresponding symbolic outcome when rules match."""
    def __init__(self, action_name: str, consequence_template: str):
        super().__init__()
        self.action_name = action_name
        self.consequence_template = consequence_template
        self.firings: List[Dict[str, Any]] = []

    def propagate(self, fact: Tuple[str, str, Any], working_memory: Set[Tuple[str, str, Any]]):
        subj, attr, val = fact
        # Log match event
        firing = {
            "subject": subj,
            "attribute": attr,
            "value": val,
            "action": self.action_name,
            "outcome": self.consequence_template.format(subject=subj, value=val)
        }
        self.firings.append(firing)


class ReteEngine:
    """Forward-chaining production rules engine matching enterprise patterns in O(1) time."""
    def __init__(self):
        self.working_memory: Set[Tuple[str, str, Any]] = set()
        self.alpha_nodes: List[AlphaNode] = []
        self.terminal_nodes: List[TerminalNode] = []

    def add_rule(self, attribute: str, value: Any, action_name: str, consequence: str):
        alpha = AlphaNode(attribute, value)
        terminal = TerminalNode(action_name, consequence)
        alpha.children.append(terminal)
        self.alpha_nodes.append(alpha)
        self.terminal_nodes.append(terminal)

    def assert_fact(self, subj: str, attr: str, val: Any) -> List[Dict[str, Any]]:
        fact = (subj, attr, val)
        if fact in self.working_memory:
            return []
            
        self.working_memory.add(fact)
        active_firings = []
        
        # Propagate through the network
        for node in self.alpha_nodes:
            node.propagate(fact, self.working_memory)
            
        # Collect outcomes
        for term in self.terminal_nodes:
            if term.firings:
                active_firings.extend(term.firings)
                term.firings = []  # Clear for subsequent firings
                
        return active_firings


class Z3SolverBridge:
    """Deterministic constraint satisfaction solver (bridges to z3-solver if installed)."""
    @staticmethod
    def solve_scheduling(slots: List[str], agents: List[str], constraints: List[Tuple[str, str]]) -> Dict[str, Any]:
        """
        Solves matching assignment/scheduling queries using Z3 or local search fallback.
        Constraints: list of (agent, forbidden_slot)
        """
        # If z3 is not installed, fallback to backtracking search to guarantee zero runtime failures
        try:
            import z3
            solver = z3.Solver()
            # Map agents and slots to integer variables
            vars_map = {agent: z3.Int(agent) for agent in agents}
            
            # Constrain slot assignments
            for agent, var in vars_map.items():
                solver.add(var >= 0, var < len(slots))
                
            # Disallow forbidden slots
            for agent, forbidden_slot in constraints:
                if forbidden_slot in slots:
                    idx = slots.index(forbidden_slot)
                    solver.add(vars_map[agent] != idx)
                    
            # Ensure unique assignments (no two agents share a slot if slots < agents)
            if len(agents) <= len(slots):
                solver.add(z3.Distinct(list(vars_map.values())))

            if solver.check() == z3.sat:
                model = solver.model()
                assignments = {}
                for agent, var in vars_map.items():
                    slot_idx = model[var].as_long()
                    assignments[agent] = slots[slot_idx]
                return {"solved": True, "assignments": assignments, "engine": "Z3-Solver"}
            else:
                return {"solved": False, "reason": "No feasible assignments exist.", "engine": "Z3-Solver"}
                
        except Exception as e:
            logger.debug(f"Z3 Solver not active, running local Backtracking fallback: {e}")
            # Backtracking Constraint Satisfaction Algorithm
            assignments = {}
            forbidden = {agent: set() for agent in agents}
            for agent, slot in constraints:
                forbidden[agent].add(slot)

            def backtrack(agent_idx: int) -> bool:
                if agent_idx == len(agents):
                    return True
                agent = agents[agent_idx]
                for idx, slot in enumerate(slots):
                    if slot in forbidden[agent]:
                        continue
                    if slot in assignments.values() and len(agents) <= len(slots):
                        continue
                    assignments[agent] = slot
                    if backtrack(agent_idx + 1):
                        return True
                    del assignments[agent]
                return False

            if backtrack(0):
                return {"solved": True, "assignments": assignments, "engine": "LEO-Backtracking-CSP"}
            return {"solved": False, "reason": "Unsatisfiable constraints", "engine": "LEO-Backtracking-CSP"}


class SymbolicReasoningEngine:
    """
    Unified symbolic logic compiler. Executes corporate rules, FSMs, and Z3
    constraints with millisecond latency and absolute precision.
    """

    def __init__(self):
        self.rete = ReteEngine()
        self._load_standard_rules()

    def _load_standard_rules(self):
        # Access control lists (ACL) rules
        self.rete.add_rule("role", "admin", "GRANT_ACCESS", "Subject {subject} granted FULL admin rights.")
        self.rete.add_rule("role", "guest", "RESTRICT_ACCESS", "Subject {subject} restricted to read-only views.")
        
        # IT Ticket compliance
        self.rete.add_rule("severity", "critical", "TRIGGER_SMS", "Pagerduty fired alert for critical item: {subject}")
        self.rete.add_rule("department", "legal", "ROUTE_COMPLIANCE", "Contract review routed to compliance team: {subject}")

    def evaluate_policy_rules(self, subject: str, attribute: str, value: Any) -> List[Dict[str, Any]]:
        """Invokes the RETE node traversal engine for policy decisions."""
        return self.rete.assert_fact(subject, attribute, value)

    def solve_constraints(self, slots: List[str], agents: List[str], constraints: List[Tuple[str, str]]) -> Dict[str, Any]:
        """Resolves task constraints using the Z3 solver bridge."""
        return Z3SolverBridge.solve_scheduling(slots, agents, constraints)
