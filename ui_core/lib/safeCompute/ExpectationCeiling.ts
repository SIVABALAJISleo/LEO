/**
 * Expectation Ceiling Enforcer
 * Locks messaging when users repeatedly demand the impossible
 * Calm, final messaging - no escalation
 */

export type DemandType = 'instant' | 'exact' | 'heavy' | 'free';

export interface ExpectationLock {
  userId: string;
  lockType: DemandType;
  lockCount: number;
  lockedAt: Date;
  lockMessage: string;
  isLocked: boolean;
}

export interface DemandEvent {
  userId: string;
  demandType: DemandType;
  timestamp: Date;
}

// Final, calm messages - no room for negotiation
const CEILING_MESSAGES: Record<DemandType, string> = {
  instant: 'This task is running at maximum speed.',
  exact: 'Full precision is being applied.',
  heavy: 'All available resources are engaged.',
  free: 'This task uses the allocated resources.',
};

const THRESHOLD_COUNTS: Record<DemandType, number> = {
  instant: 3,
  exact: 3,
  heavy: 5,
  free: 5,
};

const LOCK_DURATION_MS = 5 * 60 * 1000; // 5 minutes

class ExpectationCeilingEnforcer {
  private static instance: ExpectationCeilingEnforcer;
  private demandHistory: Map<string, DemandEvent[]> = new Map();
  private activeLocks: Map<string, ExpectationLock> = new Map();

  static getInstance(): ExpectationCeilingEnforcer {
    if (!ExpectationCeilingEnforcer.instance) {
      ExpectationCeilingEnforcer.instance = new ExpectationCeilingEnforcer();
    }
    return ExpectationCeilingEnforcer.instance;
  }

  /**
   * Record a demand event and check if ceiling should be enforced
   */
  recordDemand(userId: string, demandType: DemandType): ExpectationLock | null {
    const event: DemandEvent = {
      userId,
      demandType,
      timestamp: new Date(),
    };

    // Add to history
    const key = `${userId}:${demandType}`;
    const history = this.demandHistory.get(key) || [];
    history.push(event);

    // Keep only recent events (last hour)
    const hourAgo = Date.now() - 60 * 60 * 1000;
    const recentHistory = history.filter(e => e.timestamp.getTime() > hourAgo);
    this.demandHistory.set(key, recentHistory);

    // Check if threshold exceeded
    const threshold = THRESHOLD_COUNTS[demandType];
    if (recentHistory.length >= threshold) {
      return this.createLock(userId, demandType, recentHistory.length);
    }

    // Check for existing lock
    const existingLock = this.getLock(userId, demandType);
    if (existingLock?.isLocked) {
      return existingLock;
    }

    return null;
  }

  /**
   * Check if user has an active lock for a demand type
   */
  isLocked(userId: string, demandType: DemandType): boolean {
    const lock = this.getLock(userId, demandType);
    return lock?.isLocked ?? false;
  }

  /**
   * Get the ceiling message for a locked demand
   */
  getCeilingMessage(userId: string, demandType: DemandType): string | null {
    const lock = this.getLock(userId, demandType);
    if (lock?.isLocked) {
      return lock.lockMessage;
    }
    return null;
  }

  /**
   * Get all active locks for a user
   */
  getUserLocks(userId: string): ExpectationLock[] {
    const locks: ExpectationLock[] = [];
    
    for (const [key, lock] of this.activeLocks) {
      if (key.startsWith(userId) && lock.isLocked) {
        // Check if lock has expired
        if (this.isLockExpired(lock)) {
          this.activeLocks.delete(key);
        } else {
          locks.push(lock);
        }
      }
    }

    return locks;
  }

  /**
   * Clear all locks for a user (admin action)
   */
  clearUserLocks(userId: string): void {
    for (const key of this.activeLocks.keys()) {
      if (key.startsWith(userId)) {
        this.activeLocks.delete(key);
      }
    }
  }

  /**
   * Get demand count for a user and type
   */
  getDemandCount(userId: string, demandType: DemandType): number {
    const key = `${userId}:${demandType}`;
    const history = this.demandHistory.get(key) || [];
    
    const hourAgo = Date.now() - 60 * 60 * 1000;
    return history.filter(e => e.timestamp.getTime() > hourAgo).length;
  }

  /**
   * Get remaining demands before lock
   */
  getRemainingDemands(userId: string, demandType: DemandType): number {
    const count = this.getDemandCount(userId, demandType);
    const threshold = THRESHOLD_COUNTS[demandType];
    return Math.max(0, threshold - count);
  }

  /**
   * Manually unlock (for user who accepted the reality)
   */
  acknowledge(userId: string, demandType: DemandType): void {
    const key = `${userId}:${demandType}`;
    this.activeLocks.delete(key);
  }

  // Private methods

  private getLock(userId: string, demandType: DemandType): ExpectationLock | null {
    const key = `${userId}:${demandType}`;
    const lock = this.activeLocks.get(key);

    if (lock && this.isLockExpired(lock)) {
      this.activeLocks.delete(key);
      return null;
    }

    return lock ?? null;
  }

  private createLock(userId: string, demandType: DemandType, count: number): ExpectationLock {
    const lock: ExpectationLock = {
      userId,
      lockType: demandType,
      lockCount: count,
      lockedAt: new Date(),
      lockMessage: CEILING_MESSAGES[demandType],
      isLocked: true,
    };

    const key = `${userId}:${demandType}`;
    this.activeLocks.set(key, lock);

    return lock;
  }

  private isLockExpired(lock: ExpectationLock): boolean {
    return Date.now() - lock.lockedAt.getTime() > LOCK_DURATION_MS;
  }
}

export const expectationCeiling = ExpectationCeilingEnforcer.getInstance();
