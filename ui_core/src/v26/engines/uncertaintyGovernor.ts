// V26 — Phase 3 Uncertainty Governor
// Estimates model certainty to prevent false confidence. Outputs are classified dynamically.

export type UncertaintyClass = "Verified" | "Likely" | "Uncertain" | "Unknown";

export interface UncertaintyResolution {
  uncertaintyClass: UncertaintyClass;
  confidenceScore: number;
  evidenceCitationsCount: number;
  unknownAreas: string[];
  verificationStatus: "VERIFIED_PASS" | "UNCALIBRATED_WARNING";
}

export class UncertaintyGovernor {
  assess(query: string, compositeAccuracy: number, citationCount: number): UncertaintyResolution {
    const hasUnk = /unknown|contradict/i.test(query);

    let uncertaintyClass: UncertaintyClass = "Verified";
    let confidenceScore = compositeAccuracy;
    let verificationStatus: UncertaintyResolution['verificationStatus'] = "VERIFIED_PASS";
    const unknownAreas: string[] = [];

    if (hasUnk || citationCount === 0) {
      uncertaintyClass = "Unknown";
      confidenceScore = 0.25;
      verificationStatus = "UNCALIBRATED_WARNING";
      unknownAreas.push("Target parameters contain empty citation indexes.");
    } else if (compositeAccuracy < 0.80) {
      uncertaintyClass = "Uncertain";
      verificationStatus = "UNCALIBRATED_WARNING";
      unknownAreas.push("Platform aggregated accuracy fell below 80% threshold.");
    } else if (compositeAccuracy < 0.95) {
      uncertaintyClass = "Likely";
    }

    return {
      uncertaintyClass,
      confidenceScore: parseFloat(confidenceScore.toFixed(3)),
      evidenceCitationsCount: citationCount,
      unknownAreas,
      verificationStatus
    };
  }
}
