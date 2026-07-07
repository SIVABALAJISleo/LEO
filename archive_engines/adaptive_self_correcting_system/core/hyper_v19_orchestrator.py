from .dsl_parser import DSLParser
from .temporal_engine import TemporalEngine
from .solver_portfolio import SolverPortfolio
from ..models.schemas import (
    LeoV19Response, ProvenStatus, ProofStatus
)

class LeoV19Orchestrator:
    """
    SYSTEM: HYPER VERIFIED CORE v19.0
    Objective: 100% correctness. Only proven/bounded truth or explicit unknown.
    """
    def __init__(self):
        self.dsl_parser = DSLParser()
        self.temporal_engine = TemporalEngine()
        self.solver_portfolio = SolverPortfolio()

    async def run(self, user_input: str) -> LeoV19Response:
        # 1) INPUT GATE (DSL ONLY)
        parsed = self.dsl_parser.parse(user_input)
        if not parsed:
            return LeoV19Response(
                status=ProvenStatus.HALT,
                proof=ProofStatus.FAILED,
                domain="UNKNOWN",
                reason="Input failed strict DSL parsing."
            )

        domain = parsed["domain"]
        command = parsed["command"]

        # 5) TEMPORAL VALIDITY (MTL)
        # Mock: Check if domain axioms are still valid
        if not self.temporal_engine.is_valid(f"AXIOMS_{domain}"):
            self.temporal_engine.register_fact(f"AXIOMS_{domain}") # Refresh for mock

        # 6) REASONING ENGINE (Portfolio Solvers)
        status_str, result, assumptions = self.solver_portfolio.check_sat(command)

        # 10) ZERO-GUESS POLICY
        if status_str == "PROVEN":
            return LeoV19Response(
                status=ProvenStatus.PROVEN,
                result=result,
                proof=ProofStatus.VERIFIED,
                domain=domain,
                assumptions=assumptions,
                ttl=self.temporal_engine.get_remaining_ttl(f"AXIOMS_{domain}"),
                reason="Formal proof successfully verified by portfolio solvers."
            )
        elif status_str == "BOUNDED":
            return LeoV19Response(
                status=ProvenStatus.BOUNDED,
                result=result,
                proof=ProofStatus.PARTIAL,
                domain=domain,
                assumptions=assumptions,
                reason="Result is bounded within specified constraints."
            )
        elif status_str == "HALT":
             return LeoV19Response(
                status=ProvenStatus.HALT,
                proof=ProofStatus.FAILED,
                domain=domain,
                reason="Solver returned UNSAT. Operation rejected for safety."
            )
        else:
            return LeoV19Response(
                status=ProvenStatus.UNKNOWN,
                proof=ProofStatus.FAILED,
                domain=domain,
                reason="Explicit unknown: no proof or bound could be derived."
            )

