// StateCompressor - State Compression & Resilience
// Deterministic execution, replayable inputs
// Continuous checkpointing
// Crash = resume, shutdown = pause

interface CheckpointData {
  id: string;
  jobId: string;
  progress: number;
  state: unknown;
  inputs: unknown;
  createdAt: Date;
  version: number;
}

interface QueueState {
  jobs: { id: string; status: string; priority: number }[];
  lastUpdated: Date;
}

interface SystemState {
  queue: QueueState;
  activeJobs: string[];
  completedToday: number;
  failedToday: number;
}

class StateCompressor {
  private readonly STORAGE_KEY = "hyper_state_checkpoint";
  private readonly CHECKPOINT_INTERVAL = 5000; // 5 seconds
  private checkpoints: Map<string, CheckpointData> = new Map();
  private systemState: SystemState | null = null;
  private intervalId: ReturnType<typeof setInterval> | null = null;
  private isDirty = false;

  constructor() {
    this.loadFromStorage();
    this.startAutoSave();
    this.setupBeforeUnload();
  }

  // Create checkpoint for a job
  checkpoint(jobId: string, progress: number, state: unknown, inputs: unknown): string {
    const existing = this.checkpoints.get(jobId);
    const version = existing ? existing.version + 1 : 1;

    const checkpoint: CheckpointData = {
      id: `cp-${jobId}-${version}`,
      jobId,
      progress,
      state,
      inputs,
      createdAt: new Date(),
      version,
    };

    this.checkpoints.set(jobId, checkpoint);
    this.isDirty = true;

    return checkpoint.id;
  }

  // Get latest checkpoint for a job
  getCheckpoint(jobId: string): CheckpointData | null {
    return this.checkpoints.get(jobId) || null;
  }

  // Can resume from checkpoint?
  canResume(jobId: string): boolean {
    const checkpoint = this.checkpoints.get(jobId);
    return !!checkpoint && checkpoint.progress < 100;
  }

  // Get resume point
  getResumePoint(jobId: string): { progress: number; state: unknown } | null {
    const checkpoint = this.checkpoints.get(jobId);
    if (!checkpoint) return null;

    return {
      progress: checkpoint.progress,
      state: checkpoint.state,
    };
  }

  // Update system state
  updateSystemState(state: Partial<SystemState>): void {
    this.systemState = {
      ...this.systemState,
      queue: state.queue || this.systemState?.queue || { jobs: [], lastUpdated: new Date() },
      activeJobs: state.activeJobs || this.systemState?.activeJobs || [],
      completedToday: state.completedToday ?? this.systemState?.completedToday ?? 0,
      failedToday: state.failedToday ?? this.systemState?.failedToday ?? 0,
    };
    this.isDirty = true;
  }

  // Get system state
  getSystemState(): SystemState | null {
    return this.systemState;
  }

  // Save to localStorage
  private saveToStorage(): void {
    if (!this.isDirty) return;

    try {
      const data = {
        checkpoints: Array.from(this.checkpoints.entries()),
        systemState: this.systemState,
        savedAt: new Date().toISOString(),
      };
      localStorage.setItem(this.STORAGE_KEY, JSON.stringify(data));
      this.isDirty = false;
    } catch (e) {
      console.warn("Failed to save state checkpoint:", e);
    }
  }

  // Load from localStorage
  private loadFromStorage(): void {
    try {
      const stored = localStorage.getItem(this.STORAGE_KEY);
      if (!stored) return;

      const data = JSON.parse(stored);

      // Restore checkpoints
      if (Array.isArray(data.checkpoints)) {
        this.checkpoints = new Map(
          data.checkpoints.map(([k, v]: [string, CheckpointData]) => [
            k,
            { ...v, createdAt: new Date(v.createdAt) },
          ]),
        );
      }

      // Restore system state
      if (data.systemState) {
        this.systemState = {
          ...data.systemState,
          queue: {
            ...data.systemState.queue,
            lastUpdated: new Date(data.systemState.queue?.lastUpdated || Date.now()),
          },
        };
      }

      console.log("Restored state from checkpoint:", {
        checkpoints: this.checkpoints.size,
        hasSystemState: !!this.systemState,
      });
    } catch (e) {
      console.warn("Failed to load state checkpoint:", e);
    }
  }

  // Start auto-save interval
  private startAutoSave(): void {
    this.intervalId = setInterval(() => {
      this.saveToStorage();
    }, this.CHECKPOINT_INTERVAL);
  }

  // Setup beforeunload handler
  private setupBeforeUnload(): void {
    if (typeof window !== "undefined") {
      window.addEventListener("beforeunload", () => {
        this.saveToStorage();
      });

      // Also save on visibility change (tab hidden)
      document.addEventListener("visibilitychange", () => {
        if (document.visibilityState === "hidden") {
          this.saveToStorage();
        }
      });
    }
  }

  // Force save
  forceSave(): void {
    this.isDirty = true;
    this.saveToStorage();
  }

  // Clear checkpoint for job
  clearCheckpoint(jobId: string): void {
    this.checkpoints.delete(jobId);
    this.isDirty = true;
  }

  // Clear all checkpoints
  clearAll(): void {
    this.checkpoints.clear();
    this.systemState = null;
    this.isDirty = true;
    localStorage.removeItem(this.STORAGE_KEY);
  }

  // Get checkpoint stats
  getStats(): {
    checkpointCount: number;
    oldestCheckpoint: Date | null;
    totalStateSize: number;
  } {
    const checkpoints = Array.from(this.checkpoints.values());
    const oldest = checkpoints.reduce(
      (min, cp) => (cp.createdAt < min ? cp.createdAt : min),
      new Date(),
    );

    const stateJson = JSON.stringify({
      checkpoints: Array.from(this.checkpoints.entries()),
      systemState: this.systemState,
    });

    return {
      checkpointCount: this.checkpoints.size,
      oldestCheckpoint: checkpoints.length > 0 ? oldest : null,
      totalStateSize: new Blob([stateJson]).size,
    };
  }

  // Cleanup old checkpoints (keep only latest per job)
  cleanup(): void {
    // Current implementation already keeps only latest per job
    // This method is for future expansion
    this.saveToStorage();
  }

  // Stop auto-save (for cleanup)
  dispose(): void {
    if (this.intervalId) {
      clearInterval(this.intervalId);
      this.intervalId = null;
    }
    this.saveToStorage();
  }
}

export const stateCompressor = new StateCompressor();
