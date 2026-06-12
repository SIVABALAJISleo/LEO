// LEO AI V32 — Phase 4 Automatic Contradiction Resolution Engine
// Process: Knowledge A vs Knowledge B.
// Evaluate: evidence quality, source authority, freshness, outcome success.
// Resolve: replace, merge, quarantine, flag.

export interface KnowledgeNode {
  id: string;
  statement: string;
  sourceAuthority: number; // 0 to 10
  freshnessTimestamp: number;
  historicalSuccessCount: number;
}

export interface ResolutionVerdict {
  nodeAId: string;
  nodeBId: string;
  resolutionAction: "Replace_A_With_B" | "Replace_B_With_A" | "Merge_Fields" | "Quarantine_Both" | "Flag_For_Human";
  reasoning: string;
  verifiedKnowledgeState: string;
}

export class ContradictionResolutionEngine {
  resolveConflict(a: KnowledgeNode, b: KnowledgeNode): ResolutionVerdict {
    // Score factors
    const scoreA = a.sourceAuthority * 0.4 + (a.historicalSuccessCount * 0.3) + (a.freshnessTimestamp * 0.0000000001 * 0.3);
    const scoreB = b.sourceAuthority * 0.4 + (b.historicalSuccessCount * 0.3) + (b.freshnessTimestamp * 0.0000000001 * 0.3);

    let resolutionAction: "Replace_A_With_B" | "Replace_B_With_A" | "Merge_Fields" | "Quarantine_Both" | "Flag_For_Human" = "Flag_For_Human";
    let reasoning = "";
    let verifiedKnowledgeState = "";

    const scoreDiff = Math.abs(scoreA - scoreB);

    if (scoreDiff > 4.0) {
      if (scoreA > scoreB) {
        resolutionAction = "Replace_B_With_A";
        reasoning = `Node A has significantly higher authority (${a.sourceAuthority}) and history than Node B (${b.sourceAuthority}).`;
        verifiedKnowledgeState = a.statement;
      } else {
        resolutionAction = "Replace_A_With_B";
        reasoning = `Node B has significantly higher authority (${b.sourceAuthority}) and history than Node A (${a.sourceAuthority}).`;
        verifiedKnowledgeState = b.statement;
      }
    } else if (a.statement.toLowerCase().trim() === b.statement.toLowerCase().trim()) {
      resolutionAction = "Merge_Fields";
      reasoning = "Statements are semantically identical. Merging usage counts.";
      verifiedKnowledgeState = a.statement;
    } else if (Math.abs(a.freshnessTimestamp - b.freshnessTimestamp) < 3600 * 24 * 1000) {
      // Very close timestamps and comparable authority => flag/quarantine
      resolutionAction = "Quarantine_Both";
      reasoning = "High contradiction parity with similar timestamps and authority levels. Quarantining nodes.";
      verifiedKnowledgeState = `[QUARANTINED CONTRADICTION] Option A: "${a.statement}" vs Option B: "${b.statement}"`;
    } else {
      // Prefer fresher node
      if (a.freshnessTimestamp > b.freshnessTimestamp) {
        resolutionAction = "Replace_B_With_A";
        reasoning = `Preferring Node A as it is fresher by ${Math.round((a.freshnessTimestamp - b.freshnessTimestamp) / 3600000)} hours.`;
        verifiedKnowledgeState = a.statement;
      } else {
        resolutionAction = "Replace_A_With_B";
        reasoning = `Preferring Node B as it is fresher by ${Math.round((b.freshnessTimestamp - a.freshnessTimestamp) / 3600000)} hours.`;
        verifiedKnowledgeState = b.statement;
      }
    }

    return {
      nodeAId: a.id,
      nodeBId: b.id,
      resolutionAction,
      reasoning,
      verifiedKnowledgeState
    };
  }
}
