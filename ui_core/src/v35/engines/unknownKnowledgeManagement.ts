// LEO AI V35 — Unknown Knowledge Management Engine
// Manages uncertainty states and triggers retrieval actions instead of making predictions to prevent hallucinations.

import { OutputCategory } from "./retrievalFirstIntelligence";

export interface VerificationTrigger {
  workflowId: string;
  queryTopic: string;
  sourceTarget: string;
  launchedTimestamp: number;
}

export interface UncertaintyResolution {
  currentCategory: OutputCategory;
  isHallucinatingRisk: boolean;
  prescribedMitigation: string;
  evidenceWorkflowLaunched: boolean;
  triggers: VerificationTrigger[];
}

export class UnknownKnowledgeManagement {
  private activeWorkflows: VerificationTrigger[] = [];

  /**
   * Evaluates if a statement has high uncertainty or lack of records, launching retrieval searches.
   */
  public manageUncertainty(topic: string, currentCategory: OutputCategory): UncertaintyResolution {
    let isHallucinatingRisk = false;
    let prescribedMitigation = "Output matches verified reference documents.";
    let evidenceWorkflowLaunched = false;

    if (currentCategory === "Unknown" || currentCategory === "Uncertain") {
      isHallucinatingRisk = true;
      prescribedMitigation =
        "Do not predict output. Halt token generation and launch verification crawlers.";

      // Launch a new verification crawler task if not already registered
      const exists = this.activeWorkflows.some(
        (w) => w.queryTopic.toLowerCase() === topic.toLowerCase(),
      );

      if (!exists) {
        const newTrigger: VerificationTrigger = {
          workflowId: `wf-${(1000 + Math.random() * 9000).toFixed(0)}`,
          queryTopic: topic,
          sourceTarget: "arxiv.org/semantic_scholar/google_search",
          launchedTimestamp: Date.now(),
        };
        this.activeWorkflows.push(newTrigger);
        evidenceWorkflowLaunched = true;
      }
    } else if (currentCategory === "Likely") {
      prescribedMitigation =
        "Proceed with caution. Request confidence confirmation from user before finalizing.";
    }

    return {
      currentCategory,
      isHallucinatingRisk,
      prescribedMitigation,
      evidenceWorkflowLaunched,
      triggers: [...this.activeWorkflows],
    };
  }

  /**
   * Resets active crawls list.
   */
  public clearWorkflows(): void {
    this.activeWorkflows = [];
  }
}
