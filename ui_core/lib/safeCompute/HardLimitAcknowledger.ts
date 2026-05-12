/**
 * Hard Limit Acknowledger
 * Detect and gracefully handle true physical/computational limits
 * No theory shown - calm UX only
 */

export type HardLimitType =
  | 'fresh_private_heavy'
  | 'zero_wait_impossible'
  | 'expectation_mismatch'
  | 'resource_exhausted'
  | 'thermal_limit'
  | 'memory_limit';

export interface HardLimitDetection {
  detected: boolean;
  limitType: HardLimitType | null;
  userMessage: string;
  suggestedAction: string;
  canRetry: boolean;
  retryDelay?: number;
}

export interface LimitCheckInput {
  isFresh: boolean;
  isPrivate: boolean;
  isHeavy: boolean;
  requestedWaitTime: number; // in seconds, 0 = instant
  availableMemoryMB: number;
  currentTemperature: number;
  queueDepth: number;
  userExpectation: 'instant' | 'fast' | 'normal' | 'patient';
}

// User-friendly messages - no technical details
const LIMIT_MESSAGES: Record<HardLimitType, { message: string; action: string }> = {
  fresh_private_heavy: {
    message: 'This request needs dedicated processing time.',
    action: 'We\'ll notify you when it\'s ready.',
  },
  zero_wait_impossible: {
    message: 'This task requires a few moments to complete.',
    action: 'View estimated completion time.',
  },
  expectation_mismatch: {
    message: 'This request is more complex than expected.',
    action: 'Choose a faster option or wait for full results.',
  },
  resource_exhausted: {
    message: 'The system is handling many requests.',
    action: 'Your request is queued and will start soon.',
  },
  thermal_limit: {
    message: 'Processing is temporarily slowed for stability.',
    action: 'Your request will continue automatically.',
  },
  memory_limit: {
    message: 'This request needs more resources.',
    action: 'Try a smaller request or wait for resources.',
  },
};

class HardLimitAcknowledgerEngine {
  private static instance: HardLimitAcknowledgerEngine;

  // Configurable thresholds
  private readonly THERMAL_LIMIT = 85; // Celsius
  private readonly MEMORY_THRESHOLD_MB = 512; // Minimum available
  private readonly QUEUE_DEPTH_LIMIT = 50;
  private readonly INSTANT_THRESHOLD_SECONDS = 2;

  static getInstance(): HardLimitAcknowledgerEngine {
    if (!HardLimitAcknowledgerEngine.instance) {
      HardLimitAcknowledgerEngine.instance = new HardLimitAcknowledgerEngine();
    }
    return HardLimitAcknowledgerEngine.instance;
  }

  /**
   * Check for hard limits and return appropriate response
   */
  checkLimits(input: LimitCheckInput): HardLimitDetection {
    // Check each limit type in priority order

    // 1. Fresh + Private + Heavy = guaranteed wait
    if (input.isFresh && input.isPrivate && input.isHeavy) {
      return this.createDetection('fresh_private_heavy', true, 60);
    }

    // 2. Zero wait requested but impossible
    if (input.requestedWaitTime === 0 && input.isHeavy) {
      return this.createDetection('zero_wait_impossible', true, 30);
    }

    // 3. Thermal limits
    if (input.currentTemperature >= this.THERMAL_LIMIT) {
      return this.createDetection('thermal_limit', true, 120);
    }

    // 4. Memory limits
    if (input.availableMemoryMB < this.MEMORY_THRESHOLD_MB && input.isHeavy) {
      return this.createDetection('memory_limit', true, 60);
    }

    // 5. Resource exhaustion (queue depth)
    if (input.queueDepth >= this.QUEUE_DEPTH_LIMIT) {
      return this.createDetection('resource_exhausted', true, 30);
    }

    // 6. Expectation mismatch
    if (this.hasExpectationMismatch(input)) {
      return this.createDetection('expectation_mismatch', false);
    }

    // No hard limits detected
    return {
      detected: false,
      limitType: null,
      userMessage: '',
      suggestedAction: '',
      canRetry: true,
    };
  }

  /**
   * Get calm UX copy for a limit
   */
  getCalmMessage(limitType: HardLimitType): { message: string; action: string } {
    return LIMIT_MESSAGES[limitType];
  }

  /**
   * Check if a request can proceed immediately
   */
  canProceedImmediately(input: LimitCheckInput): boolean {
    const detection = this.checkLimits(input);
    return !detection.detected;
  }

  /**
   * Get estimated wait time based on conditions
   */
  getEstimatedWait(input: LimitCheckInput): { min: number; max: number; unit: 'seconds' | 'minutes' } {
    if (!input.isHeavy) {
      return { min: 1, max: 5, unit: 'seconds' };
    }

    if (input.isFresh && input.isPrivate) {
      return { min: 2, max: 10, unit: 'minutes' };
    }

    if (input.queueDepth > 20) {
      const baseWait = Math.ceil(input.queueDepth / 5);
      return { min: baseWait, max: baseWait * 2, unit: 'minutes' };
    }

    return { min: 30, max: 120, unit: 'seconds' };
  }

  /**
   * Generate user-friendly status text
   */
  getStatusText(input: LimitCheckInput): string {
    const detection = this.checkLimits(input);

    if (!detection.detected) {
      if (input.isHeavy) {
        return 'Processing your request...';
      }
      return 'Almost ready...';
    }

    return detection.userMessage;
  }

  /**
   * Determine if user should be shown alternatives
   */
  shouldShowAlternatives(input: LimitCheckInput): boolean {
    const detection = this.checkLimits(input);
    return detection.detected && detection.limitType === 'expectation_mismatch';
  }

  // Private methods

  private createDetection(
    limitType: HardLimitType,
    canRetry: boolean,
    retryDelay?: number
  ): HardLimitDetection {
    const { message, action } = LIMIT_MESSAGES[limitType];
    return {
      detected: true,
      limitType,
      userMessage: message,
      suggestedAction: action,
      canRetry,
      retryDelay,
    };
  }

  private hasExpectationMismatch(input: LimitCheckInput): boolean {
    // User expects instant but task is heavy
    if (input.userExpectation === 'instant' && input.isHeavy) {
      return true;
    }

    // User expects fast but fresh computation required
    if (input.userExpectation === 'fast' && input.isFresh && input.isHeavy) {
      return true;
    }

    return false;
  }
}

export const hardLimitAcknowledger = HardLimitAcknowledgerEngine.getInstance();
