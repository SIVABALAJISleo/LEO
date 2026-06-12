// LEO AI V34 — Contradiction Detector
// Capabilities: Flag semantic conflicts, resolve contradictory facts, and manage quarantines.

export interface ContradictionReport {
  hasConflict: boolean;
  conflictDetails?: string;
  sourceAId: string;
  sourceBId: string;
  suggestedAction: "REPLACE_OLD" | "QUARANTINE_BOTH" | "MERGE_CONCEPTS" | "NONE";
}

export class ContradictionDetector {
  detectContradiction(
    factA: { id: string; text: string; date: number },
    factB: { id: string; text: string; date: number }
  ): ContradictionReport {
    const textALower = factA.text.toLowerCase();
    const textBLower = factB.text.toLowerCase();

    // Check direct negative alignment (e.g. active vs disabled)
    let hasConflict = false;
    let conflictDetails: string | undefined;
    let suggestedAction: "REPLACE_OLD" | "QUARANTINE_BOTH" | "MERGE_CONCEPTS" | "NONE" = "NONE";

    const aContainsActive = textALower.includes("active") || textALower.includes("supported") || textALower.includes("enabled");
    const bContainsDisabled = textBLower.includes("disabled") || textBLower.includes("deprecated") || textBLower.includes("removed");

    if (aContainsActive && bContainsDisabled) {
      hasConflict = true;
      conflictDetails = `Status mismatch detected. Fact A asserts status is enabled/supported, whereas Fact B asserts status is disabled/deprecated.`;
      
      // Determine based on freshness date
      if (factA.date > factB.date) {
        suggestedAction = "REPLACE_OLD"; // Keep Fact A, replace Fact B
      } else if (factB.date > factA.date) {
        suggestedAction = "REPLACE_OLD"; // Keep Fact B, replace Fact A
      } else {
        suggestedAction = "QUARANTINE_BOTH";
      }
    }

    return {
      hasConflict,
      conflictDetails,
      sourceAId: factA.id,
      sourceBId: factB.id,
      suggestedAction
    };
  }
}
