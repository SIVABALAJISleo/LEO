// DeadlineScheduler - Deadline-aware real-time scheduling
// Estimates execution time and offers alternatives when deadlines can't be met

export type QualityLevel = 'full' | 'reduced' | 'approximate';

export interface DeadlineEstimate {
  canMeetDeadline: boolean;
  estimatedCompletionTime: number; // ms
  deadlineMs: number;
  alternatives: SchedulingAlternative[];
  recommendation: QualityLevel;
}

export interface SchedulingAlternative {
  id: string;
  quality: QualityLevel;
  label: string;
  description: string;
  estimatedTime: number; // ms
  confidenceRange: [number, number]; // e.g., [0.6, 0.8]
  available: boolean;
}

export interface JobSchedule {
  jobId: string;
  selectedQuality: QualityLevel;
  scheduledAt: Date;
  estimatedCompletion: Date;
  deadline?: Date;
}

type ScheduleListener = (schedule: JobSchedule) => void;

class DeadlineScheduler {
  private schedules: Map<string, JobSchedule> = new Map();
  private listeners: Set<ScheduleListener> = new Set();
  
  // Base execution time estimates by tier (ms)
  private readonly EXECUTION_ESTIMATES = {
    light: { base: 100, variance: 50 },
    medium: { base: 3000, variance: 2000 },
    heavy: { base: 60000, variance: 30000 },
    very_heavy: { base: 300000, variance: 120000 },
  };

  // Queue depth multiplier
  private currentQueueDepth = 0;

  // Estimate if deadline can be met
  estimateDeadline(
    jobTier: string,
    deadlineMs: number,
    memoryMb?: number
  ): DeadlineEstimate {
    const tier = jobTier as keyof typeof this.EXECUTION_ESTIMATES;
    const baseEstimate = this.EXECUTION_ESTIMATES[tier] || this.EXECUTION_ESTIMATES.heavy;
    
    // Calculate estimated time with queue consideration
    const queueDelay = this.currentQueueDepth * 5000; // 5s per queued job
    const memoryFactor = memoryMb ? Math.max(1, memoryMb / 4096) : 1;
    const estimatedTime = (baseEstimate.base + queueDelay) * memoryFactor;
    
    const canMeetDeadline = estimatedTime < deadlineMs;
    
    // Generate alternatives
    const alternatives = this.generateAlternatives(tier, estimatedTime, deadlineMs);
    
    // Determine recommendation
    let recommendation: QualityLevel = 'full';
    if (!canMeetDeadline) {
      const fastEnoughAlt = alternatives.find(a => a.available && a.estimatedTime < deadlineMs);
      recommendation = fastEnoughAlt?.quality || 'approximate';
    }

    return {
      canMeetDeadline,
      estimatedCompletionTime: estimatedTime,
      deadlineMs,
      alternatives,
      recommendation,
    };
  }

  // Schedule a job with selected quality
  scheduleJob(
    jobId: string,
    quality: QualityLevel,
    deadline?: Date
  ): JobSchedule {
    const now = new Date();
    const estimatedMs = this.getEstimatedTimeForQuality(quality);
    
    const schedule: JobSchedule = {
      jobId,
      selectedQuality: quality,
      scheduledAt: now,
      estimatedCompletion: new Date(now.getTime() + estimatedMs),
      deadline,
    };

    this.schedules.set(jobId, schedule);
    this.notifyListeners(schedule);
    
    if (quality === 'full') {
      this.currentQueueDepth++;
    }

    return schedule;
  }

  // Get schedule for a job
  getSchedule(jobId: string): JobSchedule | null {
    return this.schedules.get(jobId) ?? null;
  }

  // Mark job complete
  completeJob(jobId: string): void {
    const schedule = this.schedules.get(jobId);
    if (schedule?.selectedQuality === 'full') {
      this.currentQueueDepth = Math.max(0, this.currentQueueDepth - 1);
    }
    // Keep schedule for history
  }

  // Update queue depth from external source
  updateQueueDepth(depth: number): void {
    this.currentQueueDepth = depth;
  }

  // Get formatted time estimate
  formatTimeEstimate(ms: number): string {
    if (ms < 1000) return 'Instant';
    if (ms < 60000) return `~${Math.ceil(ms / 1000)}s`;
    if (ms < 3600000) return `~${Math.ceil(ms / 60000)} min`;
    return `~${Math.ceil(ms / 3600000)} hr`;
  }

  // Get time range estimate (conservative)
  getTimeRange(ms: number): { min: string; max: string } {
    const minMs = ms * 0.8;
    const maxMs = ms * 1.5;
    return {
      min: this.formatTimeEstimate(minMs),
      max: this.formatTimeEstimate(maxMs),
    };
  }

  // Subscribe to schedule updates
  subscribe(listener: ScheduleListener): () => void {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  private generateAlternatives(
    tier: keyof typeof this.EXECUTION_ESTIMATES,
    fullTime: number,
    deadlineMs: number
  ): SchedulingAlternative[] {
    return [
      {
        id: 'reduced',
        quality: 'reduced',
        label: 'Faster Result',
        description: 'Reduced quality for quicker delivery',
        estimatedTime: fullTime * 0.4,
        confidenceRange: [0.75, 0.85],
        available: tier !== 'light',
      },
      {
        id: 'approximate',
        quality: 'approximate',
        label: 'Quick Preview',
        description: 'Instant approximate result',
        estimatedTime: 200,
        confidenceRange: [0.6, 0.75],
        available: true,
      },
      {
        id: 'full',
        quality: 'full',
        label: 'Full Quality',
        description: fullTime < deadlineMs ? 'Complete processing' : 'Queued for later',
        estimatedTime: fullTime,
        confidenceRange: [0.92, 0.99],
        available: true,
      },
    ];
  }

  private getEstimatedTimeForQuality(quality: QualityLevel): number {
    switch (quality) {
      case 'approximate': return 200;
      case 'reduced': return 15000;
      case 'full': return 60000 + this.currentQueueDepth * 5000;
    }
  }

  private notifyListeners(schedule: JobSchedule): void {
    this.listeners.forEach(l => l(schedule));
  }
}

export const deadlineScheduler = new DeadlineScheduler();
