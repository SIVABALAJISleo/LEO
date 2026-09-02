"""
hyper_v2/api/orchestrator.py
Unified HYPER 2.0 API orchestrator connecting compiler, analyzers, autotuner, and backends.
"""

from typing import Dict, Any
from hyper_v2.compiler.contract_compiler import ContractCompiler, ExecutionContract
from hyper_v2.compiler.graph_builder import GraphBuilder
from hyper_v2.compiler.graph_optimizer import GraphOptimizer
from hyper_v2.analysis.necessity_analyzer import NecessityAnalyzer
from hyper_v2.search.autotuner import StrategyAutotuner
from hyper_v2.execution.device_manager import DeviceManager


class Hyper2Orchestrator:
    """Master entrypoint orchestrating autonomous compilation, strategy search, and execution."""

    @classmethod
    def analyze_workload(cls, payload: Dict[str, Any]) -> Dict[str, Any]:
        contract_spec = payload.get("contract", {})
        contract = ContractCompiler.compile_contract(contract_spec)
        graph = GraphBuilder.build_generic_workload_graph(contract.workload_id, payload.get("params", {}))
        report = NecessityAnalyzer.analyze_workload(graph, contract, payload.get("sample_inputs"))
        return report.to_dict()

    @classmethod
    def compile_and_plan(cls, payload: Dict[str, Any]) -> Dict[str, Any]:
        contract = ContractCompiler.compile_contract(payload.get("contract", {}))
        graph = GraphBuilder.build_generic_workload_graph(contract.workload_id, payload.get("params", {}))
        opt_graph = GraphOptimizer.optimize_graph(graph, contract)
        best_strat, all_candidates = StrategyAutotuner.select_optimal_strategy(opt_graph, contract)

        return {
            "workload_id": contract.workload_id,
            "contract_hash": contract.compute_hash(),
            "original_flops": graph.total_flops,
            "optimized_flops": opt_graph.total_flops,
            "selected_strategy": best_strat.to_dict(),
            "all_evaluated_candidates": [c.to_dict() for c in all_candidates]
        }

    @classmethod
    def get_hardware_telemetry(cls) -> Dict[str, Any]:
        import psutil
        hw = DeviceManager.get_hardware_profile()
        cpu_pct = psutil.cpu_percent(interval=None)
        mem = psutil.virtual_memory()
        return {
            "hardware_profile": hw,
            "live_telemetry": {
                "cpu_utilization_pct": cpu_pct,
                "ram_used_gb": round(mem.used / (1024 ** 3), 2),
                "ram_total_gb": round(mem.total / (1024 ** 3), 2),
                "ram_percent": mem.percent
            }
        }
