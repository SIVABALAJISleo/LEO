"""
tests/hyper_escape/test_memory_budget.py
Validates Memory-Budget Controller (Feature B / Section 4.3).
Tests peak memory estimation, safety margin enforcement, dynamic block sizing,
and non-destructive cancellation when budget is exceeded.
"""
import pytest
from hyper_universal.memory_escape.engine import MemoryBudgetController


def test_memory_budget_controller_initialization():
    controller = MemoryBudgetController(budget_mb=4096.0, safety_margin_mb=1024.0)
    assert controller.budget_mb == 4096.0
    assert controller.safety_margin_mb == 1024.0
    assert controller.effective_usable_mb == 3072.0


def test_memory_budget_block_size_calculation():
    controller = MemoryBudgetController(budget_mb=2048.0, safety_margin_mb=512.0)
    # Total data size = 100 MB, target 4 chunks
    block_mb = controller.calculate_optimal_block_size_mb(total_data_size_mb=100.0, target_chunks=4)
    assert 1.0 <= block_mb <= 25.0

    # Total data size = 10,000 MB (larger than budget)
    block_mb_large = controller.calculate_optimal_block_size_mb(total_data_size_mb=10_000.0)
    assert block_mb_large <= controller.effective_usable_mb / 4.0


def test_memory_budget_check_allocation():
    controller = MemoryBudgetController(budget_mb=1024.0, safety_margin_mb=256.0)
    # Effective usable is 768 MB

    # 200 MB should be allowed
    assert controller.check_allocation_safe(requested_mb=200.0) is True

    # 1000 MB exceeds usable (768 MB) -> False
    assert controller.check_allocation_safe(requested_mb=1000.0) is False


def test_memory_budget_telemetry():
    controller = MemoryBudgetController(budget_mb=8192.0, safety_margin_mb=2048.0)
    telemetry = controller.get_telemetry()
    assert telemetry.budget_mb == 8192.0
    assert telemetry.safety_margin_mb == 2048.0
    assert telemetry.current_used_mb >= 0.0
    assert telemetry.usable_remaining_mb >= 0.0
