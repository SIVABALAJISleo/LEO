export interface TrainingPriorityItem {
  queryText: string;
  uncertaintyScore: number;
  entropyMetric: number;
  priorityVerdict: "HighPriority_Queue" | "Normal_Queue" | "Skip_LowValue";
}
export class ActiveLearningEngine {
  private trainingQueue: TrainingPriorityItem[] = [];
  public async evaluatePriority(statement: string): Promise<TrainingPriorityItem> {
    const res = await fetch("http://localhost:8000/api/v1/v40/engines/active_learning", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ statement })
    });
    const item = await res.json();
    if (item.priorityVerdict !== "Skip_LowValue") {
      this.trainingQueue.push(item);
    }
    return item;
  }
  public getQueue(): TrainingPriorityItem[] { return this.trainingQueue; }
}
