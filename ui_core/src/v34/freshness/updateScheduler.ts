// LEO AI V34 — Update Scheduler
// Capabilities: Schedule ingestion loops, prioritize source ingestion, and track schedule queues.

export interface UpdateJob {
  jobId: string;
  targetConceptId: string;
  sourceUrl: string;
  scheduledTime: number;
  priority: "high" | "medium" | "low";
  isExecuted: boolean;
}

export class UpdateScheduler {
  private jobsList: UpdateJob[] = [];

  scheduleUpdate(conceptId: string, sourceUrl: string, priority: "high" | "medium" | "low"): UpdateJob {
    const jobId = `job-update-v34-${Math.random().toString(36).substring(7)}`;
    const job: UpdateJob = {
      jobId,
      targetConceptId: conceptId,
      sourceUrl,
      scheduledTime: Date.now() + 600000, // +10 minutes
      priority,
      isExecuted: false
    };
    this.jobsList.push(job);
    return job;
  }

  getPendingJobs(): UpdateJob[] {
    return this.jobsList.filter(j => !j.isExecuted);
  }
}
