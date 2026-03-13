// ExplainableErrors - Human-readable error explanations with next actions
// Never show "Something went wrong" or "Try again later"

export interface ExplainableError {
  code: string;
  title: string;
  explanation: string;
  nextAction: string;
  severity: 'info' | 'warning' | 'error' | 'critical';
  retryable: boolean;
  estimatedResolutionMs?: number;
  supportLink?: string;
}

export interface ErrorContext {
  userId?: string;
  jobId?: string;
  moduleName?: string;
  timestamp: string;
  requestId: string;
  originalError?: Error;
}

// Error catalog with human-readable explanations
const ERROR_CATALOG: Record<string, Omit<ExplainableError, 'code'>> = {
  // Authentication errors
  AUTH_SESSION_EXPIRED: {
    title: 'Session Expired',
    explanation: 'Your login session has expired for security reasons.',
    nextAction: 'Please log in again to continue.',
    severity: 'warning',
    retryable: false,
  },
  AUTH_INVALID_CREDENTIALS: {
    title: 'Invalid Credentials',
    explanation: 'The email or password you entered is incorrect.',
    nextAction: 'Check your credentials and try again, or reset your password.',
    severity: 'warning',
    retryable: true,
  },
  AUTH_ACCOUNT_LOCKED: {
    title: 'Account Temporarily Locked',
    explanation: 'Too many failed login attempts detected.',
    nextAction: 'Wait 15 minutes, then try again. Contact support if this persists.',
    severity: 'error',
    retryable: false,
    estimatedResolutionMs: 900000,
  },

  // Rate limiting errors
  RATE_LIMIT_EXCEEDED: {
    title: 'Rate Limit Reached',
    explanation: 'You have made too many requests in a short period.',
    nextAction: 'Wait a moment before trying again. Consider upgrading for higher limits.',
    severity: 'warning',
    retryable: true,
    estimatedResolutionMs: 60000,
  },
  DAILY_QUOTA_EXCEEDED: {
    title: 'Daily Limit Reached',
    explanation: 'You have reached your daily usage limit.',
    nextAction: 'Your quota resets at midnight UTC. Upgrade for unlimited access.',
    severity: 'warning',
    retryable: false,
  },

  // Job errors
  JOB_QUEUE_FULL: {
    title: 'Queue Capacity Reached',
    explanation: 'The system is currently processing maximum capacity.',
    nextAction: 'Your job will be queued automatically. Estimated wait: 5-10 minutes.',
    severity: 'info',
    retryable: true,
    estimatedResolutionMs: 300000,
  },
  JOB_TIMEOUT: {
    title: 'Job Timed Out',
    explanation: 'Your job took longer than the maximum allowed time.',
    nextAction: 'Try with smaller input data or simpler parameters.',
    severity: 'error',
    retryable: true,
  },
  JOB_CANCELLED: {
    title: 'Job Cancelled',
    explanation: 'This job was cancelled by user request.',
    nextAction: 'Submit a new job if you want to try again.',
    severity: 'info',
    retryable: true,
  },
  JOB_INVALID_INPUT: {
    title: 'Invalid Input Data',
    explanation: 'The input data format or values are not valid.',
    nextAction: 'Check your input against the API documentation and correct any issues.',
    severity: 'error',
    retryable: true,
    supportLink: '/documentation/api-playground',
  },

  // System errors
  SYSTEM_DEGRADED: {
    title: 'System Degraded',
    explanation: 'The system is experiencing higher than normal load.',
    nextAction: 'Operations may be slower. Non-critical features temporarily limited.',
    severity: 'warning',
    retryable: true,
  },
  SYSTEM_MAINTENANCE: {
    title: 'Scheduled Maintenance',
    explanation: 'The system is undergoing scheduled maintenance.',
    nextAction: 'Service will be restored shortly. Check status page for updates.',
    severity: 'info',
    retryable: false,
    supportLink: '/system/status',
  },
  SYSTEM_LOCKDOWN: {
    title: 'Emergency Mode Active',
    explanation: 'The system is in emergency lockdown for protection.',
    nextAction: 'Only essential operations available. We are working to restore full service.',
    severity: 'critical',
    retryable: false,
  },

  // Resource errors
  RESOURCE_NOT_FOUND: {
    title: 'Resource Not Found',
    explanation: 'The requested item does not exist or has been deleted.',
    nextAction: 'Check the ID and try again, or create a new resource.',
    severity: 'error',
    retryable: false,
  },
  RESOURCE_ACCESS_DENIED: {
    title: 'Access Denied',
    explanation: 'You do not have permission to access this resource.',
    nextAction: 'Request access from the resource owner or contact support.',
    severity: 'error',
    retryable: false,
  },

  // Payment errors (non-sensitive)
  PAYMENT_REQUIRED: {
    title: 'Upgrade Required',
    explanation: 'This feature requires a paid subscription.',
    nextAction: 'View pricing plans to unlock this feature.',
    severity: 'info',
    retryable: false,
    supportLink: '/billing/pricing',
  },
  SUBSCRIPTION_EXPIRED: {
    title: 'Subscription Expired',
    explanation: 'Your subscription has expired.',
    nextAction: 'Renew your subscription to restore access.',
    severity: 'warning',
    retryable: false,
    supportLink: '/billing/manage',
  },

  // Network errors
  NETWORK_ERROR: {
    title: 'Connection Problem',
    explanation: 'Unable to connect to the server.',
    nextAction: 'Check your internet connection and try again.',
    severity: 'error',
    retryable: true,
  },
  REQUEST_TIMEOUT: {
    title: 'Request Timed Out',
    explanation: 'The server took too long to respond.',
    nextAction: 'Try again. If this persists, the system may be under heavy load.',
    severity: 'warning',
    retryable: true,
  },

  // Validation errors
  VALIDATION_ERROR: {
    title: 'Validation Failed',
    explanation: 'The submitted data did not pass validation checks.',
    nextAction: 'Review the highlighted fields and correct any errors.',
    severity: 'warning',
    retryable: true,
  },

  // Fallback (should rarely be used)
  UNKNOWN_ERROR: {
    title: 'Unexpected Error',
    explanation: 'An unexpected error occurred that we are investigating.',
    nextAction: 'Try again in a few moments. If this persists, contact support with the request ID.',
    severity: 'error',
    retryable: true,
  },
};

class ExplainableErrorSystem {
  private static instance: ExplainableErrorSystem;

  static getInstance(): ExplainableErrorSystem {
    if (!ExplainableErrorSystem.instance) {
      ExplainableErrorSystem.instance = new ExplainableErrorSystem();
    }
    return ExplainableErrorSystem.instance;
  }

  // Create an explainable error from a code
  createError(code: string, context?: Partial<ErrorContext>): ExplainableError & ErrorContext {
    const template = ERROR_CATALOG[code] || ERROR_CATALOG.UNKNOWN_ERROR;
    
    return {
      code,
      ...template,
      userId: context?.userId,
      jobId: context?.jobId,
      moduleName: context?.moduleName,
      timestamp: context?.timestamp || new Date().toISOString(),
      requestId: context?.requestId || crypto.randomUUID(),
      originalError: context?.originalError,
    };
  }

  // Map common error types to codes
  mapErrorToCode(error: Error | unknown): string {
    if (error instanceof Error) {
      const message = error.message.toLowerCase();
      
      if (message.includes('session') || message.includes('jwt') || message.includes('token')) {
        return 'AUTH_SESSION_EXPIRED';
      }
      if (message.includes('rate limit') || message.includes('too many requests')) {
        return 'RATE_LIMIT_EXCEEDED';
      }
      if (message.includes('timeout')) {
        return 'REQUEST_TIMEOUT';
      }
      if (message.includes('network') || message.includes('fetch')) {
        return 'NETWORK_ERROR';
      }
      if (message.includes('not found') || message.includes('404')) {
        return 'RESOURCE_NOT_FOUND';
      }
      if (message.includes('permission') || message.includes('access') || message.includes('403')) {
        return 'RESOURCE_ACCESS_DENIED';
      }
      if (message.includes('validation')) {
        return 'VALIDATION_ERROR';
      }
    }

    return 'UNKNOWN_ERROR';
  }

  // Get user-friendly message
  getUserMessage(error: ExplainableError): string {
    return `${error.title}: ${error.explanation} ${error.nextAction}`;
  }

  // Check if error is retryable
  isRetryable(code: string): boolean {
    return ERROR_CATALOG[code]?.retryable ?? true;
  }

  // Get all error codes (for documentation)
  getAllCodes(): string[] {
    return Object.keys(ERROR_CATALOG);
  }

  // Get error template (for documentation)
  getTemplate(code: string): Omit<ExplainableError, 'code'> | undefined {
    return ERROR_CATALOG[code];
  }
}

export const explainableErrors = ExplainableErrorSystem.getInstance();

// Helper function for components
export function createExplainableError(
  code: string, 
  context?: Partial<ErrorContext>
): ExplainableError & ErrorContext {
  return explainableErrors.createError(code, context);
}

// Helper to convert any error to explainable
export function toExplainableError(
  error: Error | unknown, 
  context?: Partial<ErrorContext>
): ExplainableError & ErrorContext {
  const code = explainableErrors.mapErrorToCode(error);
  return explainableErrors.createError(code, {
    ...context,
    originalError: error instanceof Error ? error : undefined,
  });
}
