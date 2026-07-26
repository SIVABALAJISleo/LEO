// LEO AI V33 — Matrix Planner
// Capabilities: Select optimal multiplying algorithm based on matrix shapes, output the Math Efficiency Score.

import { WinogradEngine } from "./winogradEngine";
import { FftOptimizationEngine } from "./fftOptimizationEngine";
import { SparseMatrixEngine } from "./sparseMatrixEngine";

export interface MathSelectionReport {
  timestamp: number;
  matrixDimensions: string;
  selectedAlgorithm: "Direct Multiply" | "Winograd" | "FFT" | "Sparse Matrix" | "Block Sparse";
  opsRequired: number;
  opsSaved: number;
  mathEfficiencyScore: number; // 0 to 100
  planningOverheadMs: number;
}

export class MatrixPlanner {
  private winograd = new WinogradEngine();
  private fft = new FftOptimizationEngine();
  private sparse = new SparseMatrixEngine();

  selectOptimalAlgorithm(
    rows: number,
    cols: number,
    isSparse: boolean,
    sparsityPct = 65,
  ): MathSelectionReport {
    const startTime = performance.now();
    let selectedAlgorithm:
      "Direct Multiply" | "Winograd" | "FFT" | "Sparse Matrix" | "Block Sparse" = "Direct Multiply";
    let opsRequired = rows * cols * cols;
    let opsSaved = 0;
    let mathEfficiencyScore = 50; // base direct multiply efficiency

    if (isSparse && sparsityPct > 50) {
      selectedAlgorithm = sparsityPct > 80 ? "Sparse Matrix" : "Block Sparse";
      const report = this.sparse.evaluateSparsity(rows, cols, sparsityPct);
      opsRequired = report.activeElementsCount * cols;
      opsSaved = report.opsSaved;
      mathEfficiencyScore = sparsityPct; // efficiency aligns with the percentage of zeros skipped
    } else if (rows === 3 && cols === 3) {
      // Small 3x3 kernels are perfect for Winograd
      selectedAlgorithm = "Winograd";
      const report = this.winograd.computeWinogradSavings(64, 3);
      opsRequired = report.winogradMultiplyOps;
      opsSaved = report.operationsSaved;
      mathEfficiencyScore = report.reductionRatio * 25; // ratio 1.5x gives ~37.5 + 50
    } else if (rows > 1024) {
      // Massive matrix transforms are mapped to FFT frequency space
      selectedAlgorithm = "FFT";
      const report = this.fft.calculateFftGains(rows);
      opsRequired = report.frequencyDomainOps;
      opsSaved = report.computeSavedOps;
      // High score due to N^2 vs N log N savings
      mathEfficiencyScore = parseFloat((90.0 + report.complexityRatio * 0.1).toFixed(1));
    }

    const finalScore = parseFloat(Math.min(100, Math.max(0, mathEfficiencyScore)).toFixed(1));

    return {
      timestamp: Date.now(),
      matrixDimensions: `${rows}x${cols}`,
      selectedAlgorithm,
      opsRequired,
      opsSaved,
      mathEfficiencyScore: finalScore,
      planningOverheadMs: parseFloat((performance.now() - startTime).toFixed(3)),
    };
  }
}
