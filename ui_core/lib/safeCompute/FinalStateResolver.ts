/**
 * Final State Resolver
 * Every job MUST be in exactly ONE state at all times
 * No ambiguous states allowed
 */

export type FinalJobState =
  | 'instantly_served'
  | 'approximation_accepted'
  | 'exact_computing'
  | 'deferred_by_design'
  | 'paused_resumable'
  | 'user_cancelled';

export interface ResolvedJobState {
  jobId: string;
  state: FinalJobState;
  stateLabel: string;
  stateDescription: string;
  confidenceScore: number | null;
  isApproximate: boolean;
  checkpointAvailable: boolean;
  resolvedAt: Date;
  metadata: {
    processingMethod?: string;
    estimatedCompletion?: Date;
    pauseReason?: string;
    cancellationReason?: string;
  };
}

export interface JobStateInput {
  jobId: string;
  userId: string;
  currentStatus: string;
  isFromCache: boolean;
  isFresh: boolean;
  isHeavy: boolean;
  confidenceScore: number | null;
  hasCheckpoint: boolean;
  userAction?: 'accept_approximate' | 'wait_exact' | 'cancel';
  systemAction?: 'defer' | 'pause' | 'complete';
}

const STATE_LABELS: Record<FinalJobState, { label: string; description: string }> = {
  instantly_served: {
    label: 'Complete',
    description: 'Result delivered instantly',
  },
  approximation_accepted: {
    label: 'Quick Result',
    description: 'Fast result accepted',
  },
  exact_computing: {
    label: 'Processing',
    description: 'Full computation in progress',
  },
  deferred_by_design: {
    label: 'Scheduled',
    description: 'Queued for processing',
  },
  paused_resumable: {
    label: 'Paused',
    description: 'Can be resumed',
  },
  user_cancelled: {
    label: 'Cancelled',
    description: 'Stopped by request',
  },
};

class FinalStateResolverEngine {
  private static instance: FinalStateResolverEngine;
  private stateHistory: Map<string, ResolvedJobState[]> = new Map();

  static getInstance(): FinalStateResolverEngine {
    if (!FinalStateResolverEngine.instance) {
      FinalStateResolverEngine.instance = new FinalStateResolverEngine();
    }
    return FinalStateResolverEngine.instance;
  }

  /**
   * Resolve a job to exactly ONE final state
   * This is the single source of truth for job state
   */
  resolve(input: JobStateInput): ResolvedJobState {
    const state = this.determineState(input);
    const { label, description } = STATE_LABELS[state];

    const resolved: ResolvedJobState = {
      jobId: input.jobId,
      state,
      stateLabel: label,
      stateDescription: description,
      confidenceScore: input.confidenceScore,
      isApproximate: state === 'approximation_accepted',
      checkpointAvailable: input.hasCheckpoint,
      resolvedAt: new Date(),
      metadata: this.buildMetadata(input, state),
    };

    // Store in history
    this.addToHistory(input.jobId, resolved);

    return resolved;
  }

  /**
   * Get the current resolved state for a job
   */
  getCurrentState(jobId: string): ResolvedJobState | null {
    const history = this.stateHistory.get(jobId);
    return history && history.length > 0 ? history[history.length - 1] : null;
  }

  /**
   * Get state history for a job
   */
  getStateHistory(jobId: string): ResolvedJobState[] {
    return this.stateHistory.get(jobId) || [];
  }

  /**
   * Transition a job to a new state
   */
  transition(jobId: string, userId: string, action: 'accept_approximate' | 'wait_exact' | 'cancel' | 'pause' | 'resume'): ResolvedJobState {
    const current = this.getCurrentState(jobId);
    
    if (!current) {
      throw new Error(`No state found for job ${jobId}`);
    }

    let newInput: JobStateInput;

    switch (action) {
      case 'accept_approximate':
        newInput = {
          jobId,
          userId,
          currentStatus: 'completed',
          isFromCache: false,
          isFresh: false,
          isHeavy: false,
          confidenceScore: current.confidenceScore,
          hasCheckpoint: current.checkpointAvailable,
          userAction: 'accept_approximate',
        };
        break;

      case 'wait_exact':
        newInput = {
          jobId,
          userId,
          currentStatus: 'running',
          isFromCache: false,
          isFresh: true,
          isHeavy: true,
          confidenceScore: null,
          hasCheckpoint: current.checkpointAvailable,
          userAction: 'wait_exact',
        };
        break;

      case 'cancel':
        newInput = {
          jobId,
          userId,
          currentStatus: 'cancelled',
          isFromCache: false,
          isFresh: false,
          isHeavy: false,
          confidenceScore: null,
          hasCheckpoint: current.checkpointAvailable,
          userAction: 'cancel',
        };
        break;

      case 'pause':
        newInput = {
          jobId,
          userId,
          currentStatus: 'paused',
          isFromCache: false,
          isFresh: false,
          isHeavy: true,
          confidenceScore: current.confidenceScore,
          hasCheckpoint: true,
          systemAction: 'pause',
        };
        break;

      case 'resume':
        newInput = {
          jobId,
          userId,
          currentStatus: 'running',
          isFromCache: false,
          isFresh: true,
          isHeavy: true,
          confidenceScore: null,
          hasCheckpoint: true,
        };
        break;

      default:
        throw new Error(`Unknown action: ${action}`);
    }

    return this.resolve(newInput);
  }

  /**
   * Validate that a state transition is allowed
   */
  isValidTransition(from: FinalJobState, to: FinalJobState): boolean {
    const validTransitions: Record<FinalJobState, FinalJobState[]> = {
      instantly_served: [], // Terminal state
      approximation_accepted: [], // Terminal state
      exact_computing: ['paused_resumable', 'user_cancelled', 'instantly_served'],
      deferred_by_design: ['exact_computing', 'user_cancelled', 'paused_resumable'],
      paused_resumable: ['exact_computing', 'user_cancelled'],
      user_cancelled: [], // Terminal state
    };

    return validTransitions[from]?.includes(to) ?? false;
  }

  /**
   * Get user-friendly state summary
   */
  getStateSummary(state: FinalJobState): { icon: string; color: string; action?: string } {
    const summaries: Record<FinalJobState, { icon: string; color: string; action?: string }> = {
      instantly_served: { icon: '✓', color: 'green' },
      approximation_accepted: { icon: '⚡', color: 'blue' },
      exact_computing: { icon: '◐', color: 'primary', action: 'View Progress' },
      deferred_by_design: { icon: '◷', color: 'yellow', action: 'View Queue' },
      paused_resumable: { icon: '⏸', color: 'orange', action: 'Resume' },
      user_cancelled: { icon: '✕', color: 'gray' },
    };

    return summaries[state];
  }

  // Private methods

  private determineState(input: JobStateInput): FinalJobState {
    // User actions take precedence
    if (input.userAction === 'cancel') {
      return 'user_cancelled';
    }

    if (input.userAction === 'accept_approximate') {
      return 'approximation_accepted';
    }

    // System actions
    if (input.systemAction === 'pause') {
      return 'paused_resumable';
    }

    if (input.systemAction === 'defer') {
      return 'deferred_by_design';
    }

    // Status-based resolution
    switch (input.currentStatus) {
      case 'completed':
        if (input.isFromCache && !input.isFresh) {
          return 'instantly_served';
        }
        return input.confidenceScore !== null && input.confidenceScore < 0.9
          ? 'approximation_accepted'
          : 'instantly_served';

      case 'running':
      case 'processing':
        return 'exact_computing';

      case 'queued':
      case 'pending':
        return 'deferred_by_design';

      case 'paused':
      case 'thermal_paused':
        return 'paused_resumable';

      case 'cancelled':
      case 'failed':
        return 'user_cancelled';

      default:
        // Default to deferred if status is ambiguous
        return 'deferred_by_design';
    }
  }

  private buildMetadata(
    input: JobStateInput,
    state: FinalJobState
  ): ResolvedJobState['metadata'] {
    const metadata: ResolvedJobState['metadata'] = {};

    if (input.isFromCache) {
      metadata.processingMethod = 'cached';
    } else if (input.isHeavy) {
      metadata.processingMethod = 'fresh_compute';
    } else {
      metadata.processingMethod = 'optimized';
    }

    if (state === 'deferred_by_design' || state === 'exact_computing') {
      // Estimate completion based on typical processing time
      const estimatedMinutes = input.isHeavy ? 5 : 1;
      metadata.estimatedCompletion = new Date(Date.now() + estimatedMinutes * 60 * 1000);
    }

    if (state === 'paused_resumable') {
      metadata.pauseReason = 'System pause for optimization';
    }

    if (state === 'user_cancelled') {
      metadata.cancellationReason = input.userAction === 'cancel' 
        ? 'Cancelled by user' 
        : 'System cancellation';
    }

    return metadata;
  }

  private addToHistory(jobId: string, state: ResolvedJobState): void {
    const history = this.stateHistory.get(jobId) || [];
    history.push(state);
    
    // Keep only last 10 states per job
    if (history.length > 10) {
      history.shift();
    }
    
    this.stateHistory.set(jobId, history);
  }
}

export const finalStateResolver = FinalStateResolverEngine.getInstance();
