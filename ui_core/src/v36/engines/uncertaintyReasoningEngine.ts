// LEO AI V36 — Uncertainty Reasoning Engine
// Classifies output confidence levels to mitigate hallucinations.

import { OutputCategory } from "../../v35/v35index";

export interface ConfidenceReport {
  score: number;
  category: OutputCategory;
  ambiguityDetected: boolean;
  prescribedMitigation: string;
}

export class UncertaintyReasoningEngine {
  /**
   * Estimates uncertainty rates based on string tokens and existing facts count.
   */
  public evaluateStatement(
    statement: string,
    existingFactsCount: number
  ): ConfidenceReport {
    const sLower = statement.toLowerCase();
    
    let score = 0.96;
    let ambiguityDetected = false;
    let prescribedMitigation = "Proceed with execution.";

    if (sLower.includes("maybe") || sLower.includes("unknown") || sLower.includes("price") || existingFactsCount === 0) {
      score = 0.35;
      ambiguityDetected = true;
      prescribedMitigation = "High ambiguity detected. Stop generation and query external databases.";
    } else if (existingFactsCount < 2) {
      score = 0.72;
      prescribedMitigation = "Fuzzy match. Ask for verification prior to execution.";
    }

    let category: OutputCategory = "Verified";
    if (score < 0.4) category = "Unknown";
    else if (score < 0.6) category = "Uncertain";
    else if (score < 0.8) category = "Likely";

    return {
      score,
      category,
      ambiguityDetected,
      prescribedMitigation
    };
  }
}
