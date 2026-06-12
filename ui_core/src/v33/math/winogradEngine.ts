// LEO AI V33 — Winograd Engine
// Capabilities: Run fast Winograd convolution simulation, calculate floating point multiplication savings.

export interface WinogradStats {
  kernelSize: number; // e.g. 3 for 3x3
  directMultiplyOps: number;
  winogradMultiplyOps: number;
  operationsSaved: number;
  reductionRatio: number;
}

export class WinogradEngine {
  computeWinogradSavings(imageSize: number, kernelSize = 3): WinogradStats {
    // F(2x2, 3x3) Winograd algorithm reduces multiplication counts significantly.
    // Standard convolution for output size m=2 and filter size r=3 needs m * r multiplications per block.
    // Winograd F(2, 3) needs only 4 multiplications instead of 6.
    
    // Total blocks needed to cover the image
    const numBlocks = Math.ceil(imageSize / 2) * Math.ceil(imageSize / 2);
    
    const directMultiplyOps = numBlocks * 2 * 3; // direct F(2,3) takes 6 mults per block
    const winogradMultiplyOps = numBlocks * 4;   // Winograd takes 4 mults per block
    const operationsSaved = directMultiplyOps - winogradMultiplyOps;
    const reductionRatio = parseFloat((directMultiplyOps / winogradMultiplyOps).toFixed(2));

    return {
      kernelSize,
      directMultiplyOps,
      winogradMultiplyOps,
      operationsSaved,
      reductionRatio,
    };
  }
}
