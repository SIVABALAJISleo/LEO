// LEO AI V31 — Phase 12 Continuous Batching Engine
// Inspired by vLLM.
// Capabilities: dynamic batching, queue optimization, request merging. Maximize throughput.

export interface BatchRequest {
  id: string;
  promptLengthTokens: number;
  generatedTokensCount: number;
  maxTokens: number;
  state: "Queued" | "Prefill" | "Decoding" | "Completed";
  arrivalTimestamp: number;
}

export interface ContinuousBatchTelemetry {
  activeBatchSize: number;
  queuedRequestsCount: number;
  completedRequestsCount: number;
  averageLatencyMs: number;
  throughputTokensPerSec: number;
  mergedRequestsCount: number;
}

export class ContinuousBatchEngine {
  private queue: BatchRequest[] = [];
  private completedCount = 0;
  private mergedCount = 0;
  private maxBatchSize = 8;

  addRequest(promptLength: number, maxTokens: number): string {
    const id = `req-${Math.floor(Math.random() * 10000)}`;
    this.queue.push({
      id,
      promptLengthTokens: promptLength,
      generatedTokensCount: 0,
      maxTokens,
      state: "Queued",
      arrivalTimestamp: Date.now()
    });
    return id;
  }

  processIteration(): ContinuousBatchTelemetry {
    // 1. Merge requests that have similar prompts/prefixes (Simulate Prefix Reuse Integration)
    const activeRequests = this.queue.filter(r => r.state !== "Completed");
    const groupedPrompts: Record<number, BatchRequest[]> = {};
    activeRequests.forEach(r => {
      // Group by prompt length as a simple prefix/size similarity heuristic
      const lengthKey = r.promptLengthTokens;
      if (!groupedPrompts[lengthKey]) groupedPrompts[lengthKey] = [];
      groupedPrompts[lengthKey].push(r);
    });

    Object.entries(groupedPrompts).forEach(([_, reqs]) => {
      if (reqs.length > 1) {
        // Merge! We compress them into one processing prefix
        this.mergedCount += (reqs.length - 1);
      }
    });

    // 2. Select requests to run in active batch (Prefill + Decoding mix)
    let prefillCount = 0;
    let decodingCount = 0;
    
    let activeRunningCount = 0;
    this.queue.forEach(r => {
      if (r.state === "Completed") return;

      if (r.state === "Queued" && activeRunningCount < this.maxBatchSize) {
        r.state = "Prefill";
        prefillCount++;
        activeRunningCount++;
      } else if (r.state === "Prefill") {
        r.state = "Decoding";
        r.generatedTokensCount++;
        decodingCount++;
        activeRunningCount++;
      } else if (r.state === "Decoding") {
        r.generatedTokensCount++;
        decodingCount++;
        activeRunningCount++;
        
        if (r.generatedTokensCount >= r.maxTokens) {
          r.state = "Completed";
          this.completedCount++;
        }
      }
    });

    const activeBatchSize = prefillCount + decodingCount;
    const queuedRequestsCount = this.queue.filter(r => r.state === "Queued").length;

    // Throughput increases with batch size (continuous batching efficiency)
    const baseThroughput = 40; // tokens/sec
    const efficiencyMultiplier = 1.0 + (activeBatchSize * 0.45);
    const throughputTokensPerSec = parseFloat((baseThroughput * efficiencyMultiplier).toFixed(1));
    const averageLatencyMs = Math.round(1000 / (throughputTokensPerSec / (activeBatchSize || 1)));

    return {
      activeBatchSize,
      queuedRequestsCount,
      completedRequestsCount: this.completedCount,
      averageLatencyMs,
      throughputTokensPerSec,
      mergedRequestsCount: this.mergedCount
    };
  }

  clear(): void {
    this.queue = [];
    this.completedCount = 0;
    this.mergedCount = 0;
  }
}
