import { firebaseClient as supabase } from '@/integrations/firebase/client';

export interface LogEntry {
  message: string;
  stack?: string;
  componentName?: string;
  jobId?: string;
  moduleName?: string;
  severity?: 'info' | 'warning' | 'error' | 'critical';
  metadata?: Record<string, unknown>;
}

/**
 * Log an error to the database and optionally to an external service
 */
export async function logError(entry: LogEntry): Promise<void> {
  const {
    message,
    stack,
    componentName,
    jobId,
    moduleName,
    severity = 'error',
    metadata = {},
  } = entry;

  try {
    // Get current user if authenticated
    const { data: { user } } = await supabase.auth.getUser();
    
    // Log to Supabase
    const { error } = await supabase.from('error_logs').insert({
      user_id: user?.id || null,
      error_message: message,
      stack_trace: stack || null,
      component_name: componentName || null,
      job_id: jobId || null,
      module_name: moduleName || null,
      severity,
      metadata: {
        ...metadata,
        timestamp: new Date().toISOString(),
        url: typeof window !== 'undefined' ? window.location.href : null,
      },
    });

    if (error) {
      console.error('Failed to log error to database:', error);
    }

    // In production, you could also send to an external service like Sentry
    // if (process.env.NODE_ENV === 'production' && process.env.SENTRY_DSN) {
    //   Sentry.captureException(new Error(message), { extra: metadata });
    // }
  } catch (e) {
    // Fallback to console if logging fails
    console.error('Logging failed:', e);
    console.error('Original error:', message, stack);
  }
}

/**
 * Log a warning
 */
export async function logWarning(entry: Omit<LogEntry, 'severity'>): Promise<void> {
  return logError({ ...entry, severity: 'warning' });
}

/**
 * Log an info message
 */
export async function logInfo(entry: Omit<LogEntry, 'severity'>): Promise<void> {
  return logError({ ...entry, severity: 'info' });
}

/**
 * Create a scoped logger for a specific component
 */
export function createLogger(componentName: string) {
  return {
    error: (message: string, metadata?: Record<string, unknown>) =>
      logError({ message, componentName, metadata }),
    warning: (message: string, metadata?: Record<string, unknown>) =>
      logWarning({ message, componentName, metadata }),
    info: (message: string, metadata?: Record<string, unknown>) =>
      logInfo({ message, componentName, metadata }),
  };
}
