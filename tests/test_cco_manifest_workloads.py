"""
tests/test_cco_manifest_workloads.py
====================================
Unit tests verifying the 6 canonical manifest workloads execute correctly and satisfy their contracts.
"""

import pytest
import numpy as np
from hyper_cco.workloads import (
    Gemm512Workload,
    SpmvCsr10kWorkload,
    LlmSpeculativeWorkload,
    CbeRender720pWorkload,
    QsvMediaTranscodeWorkload,
    PdePoissonWorkload,
)


def test_gemm_512_workload():
    wl = Gemm512Workload()
    base = wl.run_baseline()
    cand = wl.run_candidate()
    passed, err_abs, err_rel = wl.verify(cand)
    assert passed is True
    assert err_rel <= 1e-3
    assert cand.shape == (512, 512)


def test_spmv_csr_10k_workload():
    wl = SpmvCsr10kWorkload()
    base = wl.run_baseline()
    cand = wl.run_candidate()
    passed, err_abs, err_rel = wl.verify(cand)
    assert passed is True
    assert err_rel <= 1e-3
    assert cand.shape == (10000,)


def test_llm_speculative_workload():
    wl = LlmSpeculativeWorkload()
    base = wl.run_baseline()
    cand = wl.run_candidate()
    passed, err_abs, err_rel = wl.verify(cand)
    assert passed is True
    assert cand.shape == (32,)
    assert np.array_equal(cand, base)


def test_cbe_render_720p_workload():
    wl = CbeRender720pWorkload()
    base = wl.run_baseline()
    cand = wl.run_candidate()
    passed, err_abs, err_rel = wl.verify(cand)
    assert passed is True
    assert cand.shape == (720, 1280, 3)


def test_qsv_media_transcode_workload():
    wl = QsvMediaTranscodeWorkload()
    base = wl.run_baseline()
    cand = wl.run_candidate()
    passed, err_abs, err_rel = wl.verify(cand)
    assert passed is True
    assert cand.shape == (10, 1080, 1920)


def test_pde_poisson_workload():
    wl = PdePoissonWorkload()
    base = wl.run_baseline()
    cand = wl.run_candidate()
    passed, err_abs, err_rel = wl.verify(cand)
    assert passed is True
    assert cand.shape == (128, 128)
