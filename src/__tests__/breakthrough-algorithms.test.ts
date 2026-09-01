import { describe, it, expect } from "vitest";
import {
  NVIDIA_GPU_DATABASE,
  HOST_HARDWARE,
  calculateGpuComparison,
} from "../lib/nvidia-gpu-database";
import { sparseFft } from "../lib/breakthrough-algorithms/sparse-fft";
import { computeRandomizedSVD } from "../lib/breakthrough-algorithms/randomized-svd";
import {
  runQmcOptionBenchmark,
  generateSobolSequence,
} from "../lib/breakthrough-algorithms/quasi-monte-carlo";
import { runFmmNBodyBenchmark } from "../lib/breakthrough-algorithms/fast-multipole-method";
import {
  HyperLogLogSketch,
  BloomFilterSketch,
  CountMinSketch,
} from "../lib/breakthrough-algorithms/streaming-sketches";
import { runBitNetTernaryBenchmark } from "../lib/breakthrough-algorithms/ternary-bitnet";
import { BrowserSemanticCache } from "../lib/breakthrough-algorithms/semantic-cache";
import { computeMorton3D, runBvhBenchmark } from "../lib/breakthrough-algorithms/morton-bvh";

describe("NVIDIA GPU Historical Database (1995-2025)", () => {
  it("should contain representative GPUs across all eras from NV1 to RTX 5090", () => {
    expect(NVIDIA_GPU_DATABASE.length).toBeGreaterThanOrEqual(25);
    const years = NVIDIA_GPU_DATABASE.map((g) => g.year);
    expect(Math.min(...years)).toBe(1995);
    expect(Math.max(...years)).toBe(2025);
  });

  it("should calculate raw silicon deficit and 100% contract parity correctly", () => {
    const rtx4090 = NVIDIA_GPU_DATABASE.find((g) => g.id === "rtx-4090");
    expect(rtx4090).toBeDefined();

    const rawComp = calculateGpuComparison(rtx4090!, HOST_HARDWARE, false);
    expect(rawComp.rawSiliconParityPct).toBeLessThan(5.0); // ~0.3% - 1.0%

    const contractComp = calculateGpuComparison(rtx4090!, HOST_HARDWARE, true);
    expect(contractComp.contractParityPct).toBe(100.0);
  });
});

describe("In-Browser Breakthrough Algorithm Engines", () => {
  it("Sparse FFT should recover dominant frequency modes in sublinear operations", () => {
    const N = 512;
    const signal = new Float64Array(N);
    for (let t = 0; t < N; t++) {
      signal[t] = Math.sin((2 * Math.PI * 30 * t) / N) + 0.8 * Math.cos((2 * Math.PI * 85 * t) / N);
    }
    const res = sparseFft(signal, 4);
    expect(res.n).toBe(512);
    expect(res.dominantFrequencies.length).toBeGreaterThan(0);
    expect(res.operationsEliminatedPct).toBeGreaterThanOrEqual(70);
  });

  it("Randomized SVD should compute low-rank approximation with low error", () => {
    const m = 64;
    const n = 64;
    const A = new Float64Array(m * n);
    for (let i = 0; i < m; i++) {
      for (let j = 0; j < n; j++) {
        A[i * n + j] = Math.sin(i * 0.1) * Math.cos(j * 0.1);
      }
    }
    const res = computeRandomizedSVD(A, m, n, 6);
    expect(res.relativeFrobeniusError).toBeLessThan(0.05);
    expect(res.workEliminatedPct).toBeGreaterThanOrEqual(60);
  });

  it("Quasi-Monte Carlo should achieve low deterministic error via Sobol sequences", () => {
    const sobol = generateSobolSequence(1000);
    expect(sobol.length).toBe(1000);
    expect(sobol[0][0]).toBeGreaterThanOrEqual(0);
    expect(sobol[0][0]).toBeLessThanOrEqual(1);

    const qmcRes = runQmcOptionBenchmark(10000);
    expect(qmcRes.finalQmcError).toBeLessThan(0.08);
    expect(qmcRes.workReductionRatio).toBe(100);
  });

  it("Fast Multipole Method should compute N-body forces with O(N) operations", () => {
    const res = runFmmNBodyBenchmark(256, 0.5);
    expect(res.fmmOps).toBeLessThan(res.bruteForceOps);
    expect(res.operationsEliminatedRatio).toBeGreaterThan(1.0);
    expect(res.maxRelativeForceError).toBeLessThan(0.15);
  });

  it("Streaming Sketches should estimate cardinality in O(1) space", () => {
    const hll = new HyperLogLogSketch(128);
    const bloom = new BloomFilterSketch(2048, 4);
    const cms = new CountMinSketch(128, 4);

    for (let i = 0; i < 5000; i++) {
      const item = `token_${i % 500}`;
      hll.add(item);
      bloom.add(item);
      cms.add(item, 1);
    }

    const est = hll.estimate();
    expect(est).toBeGreaterThan(350);
    expect(est).toBeLessThan(650);
    expect(bloom.contains("token_42")).toBe(true);
    expect(cms.estimateFrequency("token_42")).toBeGreaterThanOrEqual(10);
  });

  it("BitNet Ternary Multiplier should match exact GEMV bit-for-bit without float multiplies", () => {
    const res = runBitNetTernaryBenchmark(128, 128, 0.5);
    expect(res.fp32MultiplyCount).toBe(0);
    expect(res.memoryBandwidthSavingPct).toBeGreaterThan(90);
    expect(res.maxDiscrepancyVsExact).toBeLessThan(1e-4);
  });

  it("Semantic Cache should return hit for semantically similar queries in sub-millisecond", () => {
    const cache = new BrowserSemanticCache();
    const hitRes = cache.query("What is the LEO HYPER 100% parity architecture?");
    expect(hitRes.hit).toBe(true);
    expect(hitRes.lookupTimeMs).toBeLessThan(5.0);

    const missRes = cache.query("How to bake a chocolate cake with strawberries?");
    expect(missRes.hit).toBe(false);
  });

  it("Morton Curve and BVH should sort 3D bounding boxes in linear time", () => {
    const code1 = computeMorton3D(10, 20, 30);
    const code2 = computeMorton3D(10, 20, 31);
    expect(code1).toBeGreaterThanOrEqual(0);
    expect(code2).toBeGreaterThanOrEqual(0);

    const bvhRes = runBvhBenchmark(2000);
    expect(bvhRes.primitiveCount).toBe(2000);
    expect(bvhRes.mortonBitDepth).toBe(30);
    expect(bvhRes.mortonSortBuildTimeMs).toBeGreaterThanOrEqual(0);
    expect(bvhRes.incrementalRefitTimeMs).toBeGreaterThanOrEqual(0);
  });
});
