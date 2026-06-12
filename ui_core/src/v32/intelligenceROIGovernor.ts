// LEO AI V32 — Phase 13 Intelligence ROI Governor
// Measure: Improvement Cost (complexity/latency) vs Improvement Benefit (accuracy/safety).
// Reject: low-value complexity. Prioritize: high-impact improvements.
// Output: ROI Priority Matrix.

export interface ImprovementProposal {
  proposalId: string;
  name: string;
  estimatedAccuracyGainPct: number;
  complexityCostFactor: number; // 0 to 10 scale (lower is cheaper)
  latencyPenaltyMs: number;
  roiScore: number;
  verdict: "Prioritized" | "Approved" | "Rejected_Low_Value";
}

export class IntelligenceROIGovernor {
  evaluateProposals(proposals: { id: string; name: string; gain: number; cost: number; latency: number; }[]): ImprovementProposal[] {
    
    return proposals.map(p => {
      // ROI is proportional to gain and inversely proportional to complexity cost and latency
      const latencyFactor = p.latency > 0 ? (100 / p.latency) : 10;
      const roiScore = parseFloat(((p.gain * latencyFactor) / (p.cost || 1.0)).toFixed(2));

      let verdict: "Prioritized" | "Approved" | "Rejected_Low_Value" = "Approved";
      if (roiScore > 8.0) {
        verdict = "Prioritized";
      } else if (roiScore < 1.5 || p.cost > 8.0) {
        verdict = "Rejected_Low_Value";
      }

      return {
        proposalId: p.id,
        name: p.name,
        estimatedAccuracyGainPct: p.gain,
        complexityCostFactor: p.cost,
        latencyPenaltyMs: p.latency,
        roiScore,
        verdict
      };
    }).sort((a, b) => b.roiScore - a.roiScore);
  }
}
