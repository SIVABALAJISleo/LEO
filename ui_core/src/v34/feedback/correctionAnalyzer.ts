// LEO AI V34 — Correction Analyzer
// Capabilities: Extract error types, analyze user modifications, and identify failure coordinates.

export interface CorrectionAnalysis {
  errorType: "COMPILATION" | "LOGIC_GAP" | "RETRIEVED_FACT" | "HALLUCINATION" | "UNKNOWN";
  severity: "high" | "medium" | "low";
  rootCause: string;
  suggestedPatch: string;
}

export class CorrectionAnalyzer {
  analyzeCorrection(originalText: string, correctedText: string): CorrectionAnalysis {
    const origLower = originalText.toLowerCase();
    const corrLower = correctedText.toLowerCase();

    let errorType: "COMPILATION" | "LOGIC_GAP" | "RETRIEVED_FACT" | "HALLUCINATION" | "UNKNOWN" =
      "UNKNOWN";
    let rootCause = "Unspecified layout mismatch between original and corrected solutions.";
    let suggestedPatch = "Remediate context logic parameters.";
    let severity: "high" | "medium" | "low" = "medium";

    if (
      corrLower.includes("import") ||
      corrLower.includes("syntax") ||
      corrLower.includes("compile")
    ) {
      errorType = "COMPILATION";
      rootCause =
        "Original generated solution contains invalid import syntax or TS compiler errors.";
      suggestedPatch = "Apply AST compiler parser check before final solution stage.";
      severity = "high";
    } else if (
      corrLower.includes("not true") ||
      corrLower.includes("wrong") ||
      corrLower.includes("correct")
    ) {
      errorType = "RETRIEVED_FACT";
      rootCause = "Incorrect factual retrieval chunk referenced from local vector store.";
      suggestedPatch = "Mark relevant source URL trust score down in contradictionDetector.";
      severity = "high";
    } else if (
      corrLower.includes("logical") ||
      corrLower.includes("step") ||
      corrLower.includes("contradict")
    ) {
      errorType = "LOGIC_GAP";
      rootCause = "Reasoning chain contains logical jumps or skips steps.";
      suggestedPatch = "Increase Tree-of-Thought branch depth in distributedReasoningEngine.";
    }

    return {
      errorType,
      severity,
      rootCause,
      suggestedPatch,
    };
  }
}
