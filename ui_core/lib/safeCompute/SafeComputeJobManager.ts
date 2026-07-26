// SafeComputeJobManager - Manages local job execution
// Every user job runs INSIDE the local laptop only.
// No GPU/CPU is exposed to outside users.

import { SafeComputeJob, JobQueueStats } from "./types";

class SafeComputeJobManager {
  private jobs: Map<string, SafeComputeJob> = new Map();
  private listeners: Set<(jobs: SafeComputeJob[]) => void> = new Set();

  createJob(userId: string, priority: number = 1): SafeComputeJob {
    const job: SafeComputeJob = {
      id: crypto.randomUUID(),
      userId,
      status: "queued",
      progress: 0,
      priority,
      createdAt: new Date(),
      estimatedWaitTime: this.calculateEstimatedWait(),
      offlineCapable: true,
    };

    this.jobs.set(job.id, job);
    this.notifyListeners();
    return job;
  }

  startJob(jobId: string): boolean {
    const job = this.jobs.get(jobId);
    if (!job || job.status !== "queued") return false;

    job.status = "processing";
    job.startedAt = new Date();
    this.notifyListeners();
    return true;
  }

  updateProgress(jobId: string, progress: number): void {
    const job = this.jobs.get(jobId);
    if (job && job.status === "processing") {
      job.progress = Math.min(100, Math.max(0, progress));
      this.notifyListeners();
    }
  }

  completeJob(jobId: string, result: unknown): void {
    const job = this.jobs.get(jobId);
    if (job) {
      job.status = "completed";
      job.progress = 100;
      job.completedAt = new Date();
      job.result = result;
      this.notifyListeners();
    }
  }

  failJob(jobId: string, error: string): void {
    const job = this.jobs.get(jobId);
    if (job) {
      job.status = "failed";
      job.completedAt = new Date();
      job.error = error;
      this.notifyListeners();
    }
  }

  pauseJob(jobId: string): void {
    const job = this.jobs.get(jobId);
    if (job && job.status === "processing") {
      job.status = "paused";
      this.notifyListeners();
    }
  }

  resumeJob(jobId: string): void {
    const job = this.jobs.get(jobId);
    if (job && job.status === "paused") {
      job.status = "processing";
      this.notifyListeners();
    }
  }

  getJob(jobId: string): SafeComputeJob | undefined {
    return this.jobs.get(jobId);
  }

  getJobsByUser(userId: string): SafeComputeJob[] {
    return Array.from(this.jobs.values())
      .filter((job) => job.userId === userId)
      .sort((a, b) => b.createdAt.getTime() - a.createdAt.getTime());
  }

  getQueueStats(): JobQueueStats {
    const jobs = Array.from(this.jobs.values());
    const queued = jobs.filter((j) => j.status === "queued").length;
    const processing = jobs.filter((j) => j.status === "processing").length;
    const completed = jobs.filter((j) => j.status === "completed").length;
    const failed = jobs.filter((j) => j.status === "failed").length;

    const waitTimes = jobs
      .filter((j) => j.completedAt && j.startedAt)
      .map((j) => j.startedAt!.getTime() - j.createdAt.getTime());

    const averageWaitTime = waitTimes.length
      ? waitTimes.reduce((a, b) => a + b, 0) / waitTimes.length / 1000
      : 0;

    return {
      queued,
      processing,
      completed,
      failed,
      averageWaitTime,
      estimatedTotalWaitTime: queued * averageWaitTime,
    };
  }

  private calculateEstimatedWait(): number {
    const stats = this.getQueueStats();
    return Math.max(5, stats.queued * 10 + stats.processing * 30);
  }

  subscribe(listener: (jobs: SafeComputeJob[]) => void): () => void {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  private notifyListeners(): void {
    const jobs = Array.from(this.jobs.values());
    this.listeners.forEach((listener) => listener(jobs));
  }
}

export const safeComputeJobManager = new SafeComputeJobManager();
