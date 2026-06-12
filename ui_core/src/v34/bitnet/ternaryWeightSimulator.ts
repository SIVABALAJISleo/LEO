// LEO AI V34 — Ternary Weight Simulator
// Capabilities: Simulate mapping of floating-point weights to 1.58-bit ternary {-1, 0, 1} targets.

export interface TernarySimulationReport {
  matrixRows: number;
  matrixCols: number;
  clampedValuesPct: number; // percentage of elements mapped to non-zero values
  originalMean: number;
  simulatedMean: number;
  quantizationLossDb: number; // simulated loss in decibels
}

export class TernaryWeightSimulator {
  simulateWeightMatrix(rows: number, cols: number): TernarySimulationReport {
    const totalSize = rows * cols;
    let originalSum = 0;
    let simulatedSum = 0;
    let nonZeroCount = 0;

    // Simulate matrix values
    for (let i = 0; i < totalSize; i++) {
      const val = (Math.random() - 0.5) * 2.0; // random weight
      originalSum += val;

      // Ternary mapping threshold
      if (val > 0.4) {
        simulatedSum += 1.0;
        nonZeroCount++;
      } else if (val < -0.4) {
        simulatedSum -= 1.0;
        nonZeroCount++;
      }
    }

    const originalMean = originalSum / totalSize;
    const simulatedMean = simulatedSum / totalSize;
    const clampedValuesPct = parseFloat(((nonZeroCount / totalSize) * 100).toFixed(1));
    const quantizationLossDb = parseFloat((0.85 + Math.abs(originalMean - simulatedMean) * 4.2).toFixed(2));

    return {
      matrixRows: rows,
      matrixCols: cols,
      clampedValuesPct,
      originalMean: parseFloat(originalMean.toFixed(4)),
      simulatedMean: parseFloat(simulatedMean.toFixed(4)),
      quantizationLossDb
    };
  }
}
