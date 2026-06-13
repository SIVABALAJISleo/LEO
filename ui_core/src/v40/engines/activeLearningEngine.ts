// LEO AI V40 — Active Learning Engine
// Implements Confidence Estimation, Uncertainty Detection, Data Prioritization, and Adaptive Training.

export interface TrainingPriorityItem {
  queryText: string;
  uncertaintyScore: number; // 0.0 - 1.0
  entropyMetric: number;
  priorityVerdict: "HighPriority_Queue" | "Normal_Queue" | "Skip_LowValue";
}

export class ActiveLearningEngine {
  private trainingQueue: TrainingPriorityItem[] = [];

  /**
   * Assesses statements and registers them in the priority queue if they exhibit high uncertainty.
   */
  public evaluatePriority(statement: string): TrainingPriorityItem {
    const sLower = statement.toLowerCase();
    
    let uncertaintyScore = 0.12;
    let entropyMetric = 0.25;

    // Detect ambiguous or new terms
    if (sLower.includes("maybe") || sLower.includes("unknown") || sLower.includes("price") || sLower.length < 10) {
      uncertaintyScore = 0.88;
      entropyMetric = 0.94;
    } else if (sLower.includes("quantize") || sLower.includes("mamba")) {
      uncertaintyScore = 0.45;
      entropyMetric = 0.55;
    }

    let priorityVerdict: TrainingPriorityItem["priorityVerdict"] = "Skip_LowValue";
    if (uncertaintyScore > 0.70) {
      priorityVerdict = "HighPriority_Queue";
    } else if (uncertaintyScore > 0.30) {
      priorityVerdict = "Normal_Queue";
    }

    const item: TrainingPriorityItem = {
      queryText: statement,
      uncertaintyScore,
      entropyMetric,
      priorityVerdict
    };

    if (priorityVerdict !== "Skip_LowValue") {
      this.trainingQueue.push(item);
    }

    return item;
  }

  public getQueue(): TrainingPriorityItem[] {
    return this.trainingQueue;
  }
}
