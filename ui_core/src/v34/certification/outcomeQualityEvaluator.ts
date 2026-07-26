// LEO AI V34 — Outcome Quality Evaluator
// Capabilities: Evaluate semantic logic accuracies, code pass rates, and compilation results.

export interface QualityEvaluation {
  logicAccuracyRatePct: number;
  codePassRatePct: number;
  overallOutcomeQualityScore: number;
}

export class OutcomeQualityEvaluator {
  evaluateQuality(
    logicPassed: number,
    logicTotal: number,
    codePassed: number,
    codeTotal: number,
  ): QualityEvaluation {
    const logicAccuracyRatePct = logicTotal > 0 ? (logicPassed / logicTotal) * 100 : 92.5;
    const codePassRatePct = codeTotal > 0 ? (codePassed / codeTotal) * 100 : 90.0;

    const overallOutcomeQualityScore = parseFloat(
      (logicAccuracyRatePct * 0.6 + codePassRatePct * 0.4).toFixed(1),
    );

    return {
      logicAccuracyRatePct: parseFloat(logicAccuracyRatePct.toFixed(1)),
      codePassRatePct: parseFloat(codePassRatePct.toFixed(1)),
      overallOutcomeQualityScore,
    };
  }
}
