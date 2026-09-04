"""
tests/test_unseen_features.py
Comprehensive automated test suite for the 10 Novel Unseen Acceleration Mechanisms.
"""

import pytest
import numpy as np
import math

from hyper_mvc_dar.unseen import (
    OpKind,
    FusionStrategy,
    KernelDSLNode,
    NeuralKernelSynthesizer,
    TensorLayout,
    DifferentiableLayoutOptimizer,
    ApproxOp,
    PIErrorController,
    ApproxMode,
    ExpertTier,
    TinyMoERouter,
    MoEWorkloadGator,
    FrameType,
    TemporalChangeDetector,
    LearnedResidualPredictor,
    TemporalCoherenceEngine,
    DynamicPrecision,
    ContractAwarePrecisionScheduler,
    HeterogeneousScheduleCompiler,
    SpeculativeOutcome,
    ConfidenceEstimator,
    LatencyOptimizedSpeculativeRunner,
    PerceptualMetricCalculator,
    PerceptualEquivalenceEngine,
    TransformationRule,
    WorkloadMorpher,
    UnseenBenchmarkSuite,
)


def test_feature_1_kernel_synth():
    synth = NeuralKernelSynthesizer()
    A = np.random.randn(64, 64).astype(np.float32)
    B = np.random.randn(64, 64).astype(np.float32)
    bias = np.random.randn(64).astype(np.float32)
    inputs = {"A": A, "B": B, "bias": bias}

    nodes = [
        KernelDSLNode(op_kind=OpKind.MATMUL, inputs=["A", "B"], output="T1"),
        KernelDSLNode(op_kind=OpKind.BIAS_ADD, inputs=["T1", "bias"], output="T2"),
        KernelDSLNode(op_kind=OpKind.ACTIVATION_GELU, inputs=["T2"], output="out"),
    ]

    cand, out = synth.synthesize_and_verify(nodes, inputs)
    assert cand is not None
    assert cand.verified is True
    assert out.shape == (64, 64)

    # Verify against manual calculation
    exact = np.matmul(A, B) + bias
    exact_gelu = 0.5 * exact * (1.0 + np.tanh(np.sqrt(2.0 / np.pi) * (exact + 0.044715 * np.power(exact, 3))))
    np.testing.assert_allclose(out, exact_gelu, rtol=1e-4, atol=1e-4)


def test_feature_2_layout_optimizer():
    opt = DifferentiableLayoutOptimizer()
    shape = (4, 32, 16, 16)
    tensor = np.random.randn(*shape).astype(np.float32)

    layout, should_reformat, gain = opt.select_optimal_layout(
        tensor,
        current_layout=TensorLayout.NCHW,
        op_type="conv2d"
    )
    assert layout in (TensorLayout.NHWC, TensorLayout.BLOCKED_16C, TensorLayout.NCHW)

    # Reformat test
    nhwc = opt.reformat_tensor(tensor, TensorLayout.NCHW, TensorLayout.NHWC)
    assert nhwc.shape == (4, 16, 16, 32)

    back_nchw = opt.reformat_tensor(nhwc, TensorLayout.NHWC, TensorLayout.NCHW)
    assert back_nchw.shape == shape
    np.testing.assert_array_equal(tensor, back_nchw)


def test_feature_3_approx_op():
    controller = PIErrorController(global_error_budget=0.01)
    approx = ApproxOp(controller=controller)

    # Matmul with decaying singular values
    U, _, Vt = np.linalg.svd(np.random.randn(64, 64), full_matrices=False)
    S = np.exp(-np.arange(64) / 10.0)
    A = (U * S).dot(Vt).astype(np.float32)
    B = np.random.randn(64, 64).astype(np.float32)

    out, tel = approx.approx_matmul(A, B)
    assert out.shape == (64, 64)
    assert tel.observed_relative_error <= 0.01

    # Softmax approx
    X = np.random.randn(8, 32).astype(np.float32)
    s_out, s_tel = approx.approx_softmax(X)
    assert s_out.shape == (8, 32)
    np.testing.assert_allclose(np.sum(s_out, axis=-1), np.ones(8), rtol=1e-4, atol=1e-4)


def test_feature_4_router_moe():
    gator = MoEWorkloadGator(hidden_dim=64)
    x_simple = np.zeros(64, dtype=np.float32)
    x_simple[0] = 1.0  # low entropy, highly sparse

    out, dec = gator.execute(x_simple)
    assert out.shape == (64,)
    assert dec.tier in (ExpertTier.MICRO_EXPERT, ExpertTier.COMPACT_EXPERT, ExpertTier.FULL_DEEP_EXPERT)
    assert dec.flops_saved_ratio >= 0.0
    assert dec.router_latency_us > 0.0


def test_feature_5_temporal_gate():
    dim = 64
    full_fn = lambda x: np.maximum(0.0, np.dot(x, np.eye(dim, dtype=np.float32)))
    engine = TemporalCoherenceEngine(full_forward_fn=full_fn, dim=dim)

    # Frame 1: Keyframe
    f1 = np.ones(dim, dtype=np.float32)
    o1, t1 = engine.process_frame(f1)
    assert t1.frame_type == FrameType.KEYFRAME
    np.testing.assert_allclose(o1, f1)

    # Frame 2: Minor delta -> Residual Update
    f2 = f1 + 0.01
    o2, t2 = engine.process_frame(f2)
    assert t2.frame_type == FrameType.RESIDUAL_UPDATE
    assert t2.flops < t1.flops


def test_feature_6_precision_scheduler():
    scheduler = ContractAwarePrecisionScheduler(default_contract_error=0.01)
    scheduler.register_layer("encoder_0", 0.90)
    scheduler.register_layer("encoder_1", 0.60)
    scheduler.register_layer("encoder_2", 0.20)
    scheduler.register_layer("encoder_3", 0.15)

    res = scheduler.compute_dps_schedule(contract_error=0.01)
    assert res.contract_satisfied is True
    assert res.total_estimated_error <= 0.01
    assert res.average_bits_per_op < 32.0
    assert res.expected_speedup > 1.0

    # Test quantization simulation
    x = np.array([0.5, -0.2, 0.9, -0.8], dtype=np.float32)
    q_int8 = scheduler.quantize_simulate(x, DynamicPrecision.INT8)
    assert q_int8.shape == x.shape
    np.testing.assert_allclose(x, q_int8, atol=0.05)


def test_feature_7_schedule_compiler():
    compiler = HeterogeneousScheduleCompiler()
    sched = compiler.compile_schedule(256, 256, 256)
    assert sched.shape == (256, 256, 256)
    assert sched.tile_m > 0
    assert sched.tile_n > 0
    assert sched.tile_k > 0

    A = np.random.randn(256, 256).astype(np.float32)
    B = np.random.randn(256, 256).astype(np.float32)
    C, lat_us, used_sched = compiler.execute_scheduled_gemm(A, B, sched)
    assert C.shape == (256, 256)
    np.testing.assert_allclose(C, np.dot(A, B), rtol=1e-4, atol=1e-4)


def test_feature_8_speculative_runner():
    # High confidence draft model
    draft_fn = lambda x: np.array([0.95, 0.03, 0.02], dtype=np.float32)
    full_fn = lambda x: np.array([0.95, 0.03, 0.02], dtype=np.float32)

    runner = LatencyOptimizedSpeculativeRunner(
        draft_model_fn=draft_fn,
        full_model_fn=full_fn,
        target_slo_ms=5.0,
        base_confidence_threshold=0.60
    )

    x = np.zeros(3, dtype=np.float32)
    out, tel = runner.execute(x)
    assert tel.outcome == SpeculativeOutcome.EARLY_EXIT_ACCEPTED
    assert tel.slo_compliant is True
    assert tel.speedup > 1.0


def test_feature_9_perceptual_validator():
    engine = PerceptualEquivalenceEngine(min_ssim=0.95)

    # Identical images -> SSIM = 1.0, PSNR = 80
    img = np.ones((64, 64), dtype=np.float32) * 0.5
    ssim = PerceptualMetricCalculator.calculate_ssim(img, img)
    psnr = PerceptualMetricCalculator.calculate_psnr(img, img)
    assert ssim >= 0.999
    assert psnr >= 70.0

    # Separable substitution test on smooth texture
    x = np.linspace(0, 1, 64)
    y = np.linspace(0, 1, 64)
    xx, yy = np.meshgrid(x, y)
    smooth_img = (np.sin(xx * 5.0) * np.cos(yy * 5.0) * 0.5 + 0.5).astype(np.float32)

    res_img, res = engine.run_separable_convolution_substitution(smooth_img, kernel_size=7)
    assert res.perceptual_contract_satisfied is True
    assert res.ssim_score >= 0.95
    assert res_img.shape == (64, 64)


def test_feature_10_program_transformer():
    morpher = WorkloadMorpher(default_error_bound=0.02)
    N, d = 512, 64
    np.random.seed(42)
    Q = np.random.randn(N, d).astype(np.float32)
    K = np.random.randn(N, d).astype(np.float32)
    V = np.random.randn(N, d).astype(np.float32)

    out, res = morpher.morph_attention_to_linear(Q, K, V, error_bound=0.02, apply_positional_bias=True)
    assert res.verified_equivalent is True
    assert res.relative_error <= 0.02
    assert res.flops_reduction_ratio > 0.50
    assert out.shape == (N, d)

    # Conv2D to depthwise-separable test
    X = np.random.randn(2, 16, 16, 32).astype(np.float32)
    conv_res = morpher.morph_conv2d_to_separable(X, C_out=64, kernel_size=3)
    assert conv_res.flops_reduction_ratio > 0.80


def test_unseen_suite_benchmark():
    suite = UnseenBenchmarkSuite(iterations=2)
    records = suite.run_all()
    assert len(records) == 10
    all_compliant = all(r.contract_compliant for r in records)
    assert all_compliant is True, f"Non-compliant records: {[r.feature_id for r in records if not r.contract_compliant]}"
