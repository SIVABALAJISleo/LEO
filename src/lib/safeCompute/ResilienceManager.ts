// ResilienceManager - Single-machine resilience with checkpointing
// Ensures jobs survive power loss and can resume from last checkpoint

export interface JobCheckpoint {
  jobId: string;
  progress: number;
  state: unknown;
  checkpointedAt: Date;
  resumable: boolean;
  attemptCount: number;
}

export interface ResilienceStatus {
  activeCheckpoints: number;
  totalRecovered: number;
  lastCheckpointAt: Date | null;
}

type CheckpointListener = (checkpoint: JobCheckpoint) => void;

class ResilienceManager {
  private checkpoints: Map<string, JobCheckpoint> = new Map();
  private listeners: Set<CheckpointListener> = new Set();
  private recoveredCount = 0;
  private storageKey = 'hyper_job_checkpoints';

  constructor() {
    this.loadFromStorage();
    this.setupUnloadHandler();
  }

  // Create or update checkpoint for a job
  checkpoint(
    jobId: string,
    progress: number,
    state: unknown
  ): JobCheckpoint {
    const existing = this.checkpoints.get(jobId);
    
    const checkpoint: JobCheckpoint = {
      jobId,
      progress,
      state,
      checkpointedAt: new Date(),
      resumable: true,
      attemptCount: existing?.attemptCount ?? 0,
    };

    this.checkpoints.set(jobId, checkpoint);
    this.saveToStorage();
    this.notifyListeners(checkpoint);

    return checkpoint;
  }

  // Get checkpoint for a job
  getCheckpoint(jobId: string): JobCheckpoint | null {
    return this.checkpoints.get(jobId) ?? null;
  }

  // Check if job can be resumed
  canResume(jobId: string): boolean {
    const checkpoint = this.checkpoints.get(jobId);
    return checkpoint?.resumable === true && checkpoint.attemptCount < 3;
  }

  // Get resume point for a job
  getResumePoint(jobId: string): { progress: number; state: unknown } | null {
    const checkpoint = this.checkpoints.get(jobId);
    if (!checkpoint || !checkpoint.resumable) return null;
    
    return {
      progress: checkpoint.progress,
      state: checkpoint.state,
    };
  }

  // Mark job as resumed (increment attempt count)
  markResumed(jobId: string): void {
    const checkpoint = this.checkpoints.get(jobId);
    if (checkpoint) {
      checkpoint.attemptCount++;
      checkpoint.resumable = checkpoint.attemptCount < 3;
      this.saveToStorage();
      this.recoveredCount++;
    }
  }

  // Clear checkpoint after successful completion
  clearCheckpoint(jobId: string): void {
    this.checkpoints.delete(jobId);
    this.saveToStorage();
  }

  // Get all resumable jobs
  getResumableJobs(): JobCheckpoint[] {
    return Array.from(this.checkpoints.values())
      .filter(c => c.resumable);
  }

  // Get resilience status
  getStatus(): ResilienceStatus {
    const checkpointsArray = Array.from(this.checkpoints.values());
    const lastCheckpoint = checkpointsArray
      .sort((a, b) => b.checkpointedAt.getTime() - a.checkpointedAt.getTime())[0];

    return {
      activeCheckpoints: checkpointsArray.filter(c => c.resumable).length,
      totalRecovered: this.recoveredCount,
      lastCheckpointAt: lastCheckpoint?.checkpointedAt ?? null,
    };
  }

  // Mark job as not resumable (e.g., user cancelled)
  markNotResumable(jobId: string): void {
    const checkpoint = this.checkpoints.get(jobId);
    if (checkpoint) {
      checkpoint.resumable = false;
      this.saveToStorage();
    }
  }

  // Subscribe to checkpoint updates
  subscribe(listener: CheckpointListener): () => void {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  // Force save (for critical moments)
  forceSave(): void {
    this.saveToStorage();
  }

  private loadFromStorage(): void {
    try {
      const stored = localStorage.getItem(this.storageKey);
      if (stored) {
        const data = JSON.parse(stored) as { checkpoints: Array<[string, JobCheckpoint]>; recovered: number };
        this.checkpoints = new Map(
          data.checkpoints.map(([id, cp]) => [
            id,
            { ...cp, checkpointedAt: new Date(cp.checkpointedAt) }
          ])
        );
        this.recoveredCount = data.recovered || 0;
      }
    } catch (e) {
      console.warn('Failed to load checkpoints from storage:', e);
    }
  }

  private saveToStorage(): void {
    try {
      const data = {
        checkpoints: Array.from(this.checkpoints.entries()),
        recovered: this.recoveredCount,
      };
      localStorage.setItem(this.storageKey, JSON.stringify(data));
    } catch (e) {
      console.warn('Failed to save checkpoints to storage:', e);
    }
  }

  private setupUnloadHandler(): void {
    if (typeof window !== 'undefined') {
      window.addEventListener('beforeunload', () => {
        this.forceSave();
      });
    }
  }

  private notifyListeners(checkpoint: JobCheckpoint): void {
    this.listeners.forEach(l => l(checkpoint));
  }
}

export const resilienceManager = new ResilienceManager();
