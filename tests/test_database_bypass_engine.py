"""
tests/test_database_bypass_engine.py
======================================
Regression tests for the Database Query Bypass Engine.
Validates all three bypass routes (Bitmap, Aggregate, Hash GroupBy).
"""

import numpy as np
import pytest

from hyper_x.wormhole_compiler.database_bypass_engine import (
    DatabaseBypassEngine,
    BitmapIndex,
    DatabaseBypassReport,
)


def _int_col(n: int = 1000, lo: int = 0, hi: int = 99, seed: int = 0) -> np.ndarray:
    rng = np.random.default_rng(seed)
    return rng.integers(lo, hi + 1, size=n, dtype=np.int32)


class TestBitmapIndexFilter:
    def test_equality_filter_correct(self):
        col = _int_col(1000, 0, 9, seed=42)
        engine = DatabaseBypassEngine()
        result, report = engine.filter_with_bitmap(col, "eq:5", col_id="c0")
        expected = np.where(col == 5)[0]
        assert np.array_equal(result, expected)
        assert report.result_identical

    def test_range_filter_correct(self):
        col = _int_col(1000, 0, 99, seed=7)
        engine = DatabaseBypassEngine()
        result, report = engine.filter_with_bitmap(col, "range:10:30", col_id="c1")
        expected = np.where((col >= 10) & (col <= 30))[0]
        assert np.array_equal(result, expected)
        assert report.result_identical

    def test_wer_greater_than_zero_for_large_column(self):
        col = _int_col(10000, 0, 9, seed=1)
        engine = DatabaseBypassEngine()
        _, report = engine.filter_with_bitmap(col, "eq:3", col_id="large_col")
        # 10000 rows but only 10000/64 ≈ 157 word ops
        assert report.work_elimination_ratio > 0.9

    def test_report_route_name(self):
        col = _int_col(500, 0, 9, seed=3)
        engine = DatabaseBypassEngine()
        _, report = engine.filter_with_bitmap(col, "eq:2", col_id="route_check")
        assert report.route == "BITMAP_INDEX_FILTER"
        assert report.exact is True

    def test_n_selected_correct(self):
        col = _int_col(1000, 0, 9, seed=5)
        engine = DatabaseBypassEngine()
        result, report = engine.filter_with_bitmap(col, "eq:7", col_id="count_check")
        assert report.n_selected == len(result)

    def test_empty_result_ok(self):
        col = np.zeros(500, dtype=np.int32)
        engine = DatabaseBypassEngine()
        result, report = engine.filter_with_bitmap(col, "eq:99", col_id="empty")
        assert len(result) == 0
        assert report.result_identical

    def test_all_rows_selected(self):
        col = np.ones(500, dtype=np.int32) * 42
        engine = DatabaseBypassEngine()
        result, report = engine.filter_with_bitmap(col, "eq:42", col_id="all_rows")
        assert len(result) == 500
        assert report.result_identical


class TestBitmapIndexClass:
    def test_equality_bitmap_unpack_matches_numpy(self):
        col = np.array([1, 2, 1, 3, 1, 2, 3, 1], dtype=np.int32)
        idx = BitmapIndex(col)
        bm = idx.build_equality_bitmap(1)
        unpacked = BitmapIndex.unpack_bitmap(bm, len(col))
        expected = col == 1
        assert np.array_equal(unpacked, expected)

    def test_range_bitmap_unpack_matches_numpy(self):
        col = np.arange(100, dtype=np.int32)
        idx = BitmapIndex(col)
        bm = idx.build_range_bitmap(20, 40)
        unpacked = BitmapIndex.unpack_bitmap(bm, len(col))
        expected = (col >= 20) & (col <= 40)
        assert np.array_equal(unpacked, expected)

    def test_bitmap_pads_correctly_for_non_multiple_of_64(self):
        n = 100  # Not a multiple of 64
        col = np.ones(n, dtype=np.int32)
        idx = BitmapIndex(col)
        bm = idx.build_equality_bitmap(1)
        unpacked = BitmapIndex.unpack_bitmap(bm, n)
        assert len(unpacked) == n
        assert np.all(unpacked)


class TestAggregateShortcut:
    def test_count_correct(self):
        col = _int_col(5000, 0, 100, seed=10)
        engine = DatabaseBypassEngine()
        result, report = engine.aggregate_with_shortcut(col, "count", col_id="agg_count")
        assert result == 5000
        assert report.result_identical
        assert report.route == "AGGREGATE_TILE_SHORTCUT"

    def test_sum_correct(self):
        col = _int_col(5000, 0, 100, seed=11)
        engine = DatabaseBypassEngine()
        result, report = engine.aggregate_with_shortcut(col, "sum", col_id="agg_sum")
        expected = float(np.sum(col))
        assert abs(result - expected) < 1e-3
        assert report.result_identical

    def test_min_correct(self):
        col = _int_col(5000, 0, 100, seed=12)
        engine = DatabaseBypassEngine()
        result, report = engine.aggregate_with_shortcut(col, "min", col_id="agg_min")
        expected = float(np.min(col))
        assert result == expected
        assert report.result_identical

    def test_max_correct(self):
        col = _int_col(5000, 0, 100, seed=13)
        engine = DatabaseBypassEngine()
        result, report = engine.aggregate_with_shortcut(col, "max", col_id="agg_max")
        expected = float(np.max(col))
        assert result == expected
        assert report.result_identical

    def test_wer_for_large_column(self):
        col = _int_col(100_000, 0, 100, seed=14)
        engine = DatabaseBypassEngine()
        _, report = engine.aggregate_with_shortcut(col, "sum", tile_size=256, col_id="large_agg")
        # 100000 rows / 256 = ~391 tile ops vs 100000 → WER ≈ 99.6%
        assert report.work_elimination_ratio > 0.99

    def test_tile_cache_reuse(self):
        col = _int_col(5000, 0, 100, seed=15)
        engine = DatabaseBypassEngine()
        # Build cache with sum
        engine.aggregate_with_shortcut(col, "sum", col_id="cache_reuse")
        # Second call reuses cached tiles
        _, report2 = engine.aggregate_with_shortcut(col, "min", col_id="cache_reuse")
        assert report2.result_identical


class TestHashAggregation:
    def test_sum_group_by_correct(self):
        keys = np.array([1, 2, 1, 3, 2, 1, 3, 3], dtype=np.int32)
        values = np.array([10, 20, 30, 40, 50, 60, 70, 80], dtype=np.float32)
        engine = DatabaseBypassEngine()
        result, report = engine.group_by_hash(keys, values, agg="sum")
        assert abs(result[1] - 100.0) < 1e-5   # 10+30+60
        assert abs(result[2] - 70.0) < 1e-5    # 20+50
        assert abs(result[3] - 190.0) < 1e-5   # 40+70+80
        assert report.result_identical
        assert report.route == "HASH_AGGREGATION_BYPASS"

    def test_count_group_by_correct(self):
        keys = np.array([0, 1, 0, 0, 1, 2], dtype=np.int32)
        values = np.ones(6, dtype=np.float32)
        engine = DatabaseBypassEngine()
        result, report = engine.group_by_hash(keys, values, agg="count")
        assert result[0] == 3.0
        assert result[1] == 2.0
        assert result[2] == 1.0
        assert report.result_identical

    def test_min_group_by_correct(self):
        rng = np.random.default_rng(20)
        keys = rng.integers(0, 5, size=1000, dtype=np.int32)
        values = rng.standard_normal(1000).astype(np.float32)
        engine = DatabaseBypassEngine()
        result, report = engine.group_by_hash(keys, values, agg="min")
        assert report.result_identical

    def test_wer_single_pass(self):
        keys = np.ones(10000, dtype=np.int32)
        values = np.ones(10000, dtype=np.float32)
        engine = DatabaseBypassEngine()
        _, report = engine.group_by_hash(keys, values, agg="sum")
        # Hash map is O(N) vs baseline O(2N): wer = 0.5
        assert report.work_elimination_ratio >= 0.4

    def test_report_structure(self):
        keys = np.array([1, 2, 3], dtype=np.int32)
        values = np.array([1.0, 2.0, 3.0], dtype=np.float32)
        engine = DatabaseBypassEngine()
        _, report = engine.group_by_hash(keys, values, agg="sum")
        d = report.to_dict()
        assert "route" in d
        assert "work_elimination_ratio" in d
        assert "speedup" in d
        assert "result_identical" in d
        assert d["exact"] is True


class TestDashboardIntegration:
    """Basic smoke test: all three routes fire without error and produce reports."""

    def test_three_routes_all_pass_contracts(self):
        engine = DatabaseBypassEngine()
        col = _int_col(10000, 0, 99, seed=99)

        _, r1 = engine.filter_with_bitmap(col, "eq:42", col_id="int1")
        assert r1.result_identical and r1.exact

        _, r2 = engine.aggregate_with_shortcut(col, "max", col_id="int1")
        assert r2.result_identical and r2.exact

        keys = (col % 10).astype(np.int32)
        values = col.astype(np.float32)
        _, r3 = engine.group_by_hash(keys, values, agg="sum")
        assert r3.result_identical and r3.exact
