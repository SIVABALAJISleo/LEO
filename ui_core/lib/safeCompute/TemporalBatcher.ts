// TemporalBatcher - Temporal Compression Layer
// Intentionally delays heavy jobs (30-120s window)
// Collects similar jobs, batches them, computes once, fans-out results

interface BatchedJob {
  id: string;
  signature: string;
  input: unknown;
  enqueuedAt: Date;
  callbacks: ((result: unknown) => void)[];
}

interface BatchWindow {
  signature: string;
  jobs: BatchedJob[];
  windowStart: Date;
  windowEnd: Date;
  status: "collecting" | "processing" | "completed";
}

class TemporalBatcher {
  private windows: Map<string, BatchWindow> = new Map();
  private completedResults: Map<string, unknown> = new Map();
  private windowDurationMs: number = 45000; // 45 seconds default
  private listeners: Set<(windows: BatchWindow[]) => void> = new Set();
  private processCallback?: (signature: string, input: unknown) => Promise<unknown>;

  setWindowDuration(ms: number): void {
    this.windowDurationMs = Math.max(30000, Math.min(120000, ms));
  }

  setProcessCallback(callback: (signature: string, input: unknown) => Promise<unknown>): void {
    this.processCallback = callback;
  }

  // Add job to batching window
  addJob(
    jobId: string,
    signature: string,
    input: unknown,
    onComplete: (result: unknown) => void,
  ): { windowId: string; position: number; estimatedWait: number } {
    // Check if we already have a result for this signature
    if (this.completedResults.has(signature)) {
      const result = this.completedResults.get(signature);
      // Immediate delivery
      setTimeout(() => onComplete(result), 0);
      return { windowId: signature, position: 0, estimatedWait: 0 };
    }

    let window = this.windows.get(signature);

    if (!window || window.status !== "collecting") {
      // Create new window
      const now = new Date();
      window = {
        signature,
        jobs: [],
        windowStart: now,
        windowEnd: new Date(now.getTime() + this.windowDurationMs),
        status: "collecting",
      };
      this.windows.set(signature, window);

      // Schedule window processing
      setTimeout(() => this.processWindow(signature), this.windowDurationMs);
    }

    const batchedJob: BatchedJob = {
      id: jobId,
      signature,
      input,
      enqueuedAt: new Date(),
      callbacks: [onComplete],
    };

    window.jobs.push(batchedJob);
    this.notifyListeners();

    const estimatedWait = window.windowEnd.getTime() - Date.now();

    return {
      windowId: signature,
      position: window.jobs.length,
      estimatedWait: Math.max(0, estimatedWait),
    };
  }

  // Process a batch window
  private async processWindow(signature: string): Promise<void> {
    const window = this.windows.get(signature);
    if (!window || window.status !== "collecting") return;

    window.status = "processing";
    this.notifyListeners();

    try {
      // Use the first job's input as the canonical input
      const canonicalInput = window.jobs[0]?.input;

      let result: unknown;
      if (this.processCallback) {
        result = await this.processCallback(signature, canonicalInput);
      } else {
        // Simulated processing
        await new Promise((resolve) => setTimeout(resolve, 2000));
        result = {
          signature,
          processedAt: new Date().toISOString(),
          batchSize: window.jobs.length,
          status: "success",
        };
      }

      // Cache the result
      this.completedResults.set(signature, result);

      // Fan out to all waiting jobs
      for (const job of window.jobs) {
        for (const callback of job.callbacks) {
          try {
            callback(result);
          } catch (e) {
            console.error("Callback error:", e);
          }
        }
      }

      window.status = "completed";
      this.notifyListeners();
    } catch (error) {
      // On error, notify all jobs
      for (const job of window.jobs) {
        for (const callback of job.callbacks) {
          callback({ error: String(error), status: "failed" });
        }
      }
    }
  }

  // Get current window status
  getWindowStatus(signature: string): {
    status: "none" | "collecting" | "processing" | "completed";
    jobCount: number;
    timeRemaining: number;
  } {
    const window = this.windows.get(signature);
    if (!window) {
      return { status: "none", jobCount: 0, timeRemaining: 0 };
    }

    return {
      status: window.status,
      jobCount: window.jobs.length,
      timeRemaining: Math.max(0, window.windowEnd.getTime() - Date.now()),
    };
  }

  // Get all active windows
  getActiveWindows(): BatchWindow[] {
    return Array.from(this.windows.values()).filter(
      (w) => w.status === "collecting" || w.status === "processing",
    );
  }

  // Get batching stats
  getBatchingStats(): {
    activeWindows: number;
    totalJobsBatched: number;
    averageBatchSize: number;
    totalComputesSaved: number;
  } {
    const windows = Array.from(this.windows.values());
    const completedWindows = windows.filter((w) => w.status === "completed");
    const totalJobs = completedWindows.reduce((sum, w) => sum + w.jobs.length, 0);
    const computesSaved = totalJobs - completedWindows.length;

    return {
      activeWindows: windows.filter((w) => w.status !== "completed").length,
      totalJobsBatched: totalJobs,
      averageBatchSize: completedWindows.length > 0 ? totalJobs / completedWindows.length : 0,
      totalComputesSaved: computesSaved,
    };
  }

  subscribe(listener: (windows: BatchWindow[]) => void): () => void {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  private notifyListeners(): void {
    const windows = Array.from(this.windows.values());
    this.listeners.forEach((l) => l(windows));
  }

  // Clear completed windows older than maxAgeMs
  cleanup(maxAgeMs: number = 60 * 60 * 1000): void {
    const now = Date.now();
    for (const [key, window] of this.windows.entries()) {
      if (window.status === "completed" && now - window.windowEnd.getTime() > maxAgeMs) {
        this.windows.delete(key);
      }
    }
  }
}

export const temporalBatcher = new TemporalBatcher();
