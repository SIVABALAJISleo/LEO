// OfflineJobRunner - Handles offline-first compute
// All compute runs offline-first
// If Wi-Fi drops, job STILL runs
// When internet returns, results sync automatically

import { SafeComputeJob } from "./types";

interface PendingSync {
  jobId: string;
  result: unknown;
  timestamp: Date;
}

class OfflineJobRunner {
  private isOnline: boolean = navigator.onLine;
  private pendingSyncs: Map<string, PendingSync> = new Map();
  private listeners: Set<(online: boolean, pending: number) => void> = new Set();

  constructor() {
    // Monitor network status
    if (typeof window !== "undefined") {
      window.addEventListener("online", () => this.handleOnline());
      window.addEventListener("offline", () => this.handleOffline());
    }
  }

  private handleOnline(): void {
    this.isOnline = true;
    this.syncPendingResults();
    this.notifyListeners();
  }

  private handleOffline(): void {
    this.isOnline = false;
    this.notifyListeners();
  }

  getOnlineStatus(): boolean {
    return this.isOnline;
  }

  getPendingSyncCount(): number {
    return this.pendingSyncs.size;
  }

  // Queue result for sync when back online
  queueForSync(jobId: string, result: unknown): void {
    this.pendingSyncs.set(jobId, {
      jobId,
      result,
      timestamp: new Date(),
    });

    if (this.isOnline) {
      this.syncPendingResults();
    }

    this.notifyListeners();
  }

  // Sync all pending results when back online
  async syncPendingResults(): Promise<void> {
    if (!this.isOnline || this.pendingSyncs.size === 0) return;

    const syncs = Array.from(this.pendingSyncs.entries());

    for (const [jobId, sync] of syncs) {
      try {
        // In production, would make API call here
        console.log(`Syncing result for job ${jobId}`, sync.result);

        // Remove from pending after successful sync
        this.pendingSyncs.delete(jobId);
      } catch (error) {
        console.error(`Failed to sync job ${jobId}:`, error);
        // Keep in pending for retry
      }
    }

    this.notifyListeners();
  }

  // Check if job can run offline
  canRunOffline(job: SafeComputeJob): boolean {
    return job.offlineCapable;
  }

  // Store job result locally for offline access
  storeLocalResult(jobId: string, result: unknown): void {
    try {
      const key = `hyper_job_result_${jobId}`;
      localStorage.setItem(
        key,
        JSON.stringify({
          result,
          timestamp: new Date().toISOString(),
        }),
      );
    } catch (error) {
      console.error("Failed to store local result:", error);
    }
  }

  // Retrieve locally stored result
  getLocalResult(jobId: string): unknown | null {
    try {
      const key = `hyper_job_result_${jobId}`;
      const stored = localStorage.getItem(key);
      if (stored) {
        return JSON.parse(stored).result;
      }
    } catch (error) {
      console.error("Failed to retrieve local result:", error);
    }
    return null;
  }

  subscribe(listener: (online: boolean, pending: number) => void): () => void {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  private notifyListeners(): void {
    this.listeners.forEach((listener) => listener(this.isOnline, this.pendingSyncs.size));
  }
}

export const offlineJobRunner = new OfflineJobRunner();
