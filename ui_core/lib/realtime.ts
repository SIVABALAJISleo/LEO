// ============================================
// Real-time Subscription Helpers (Mock - Supabase Removed)
// ============================================

import type {
  InferenceJob,
  PerformanceMetric,
  Alert,
  ModuleStatus,
  RealtimePayload,
  UnsubscribeFn,
  SystemMetrics,
} from "./types";

// ============================================
// Generic Subscription Helper (Mock)
// ============================================

function createMockSubscription<T>(
  table: string,
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  callback: (payload: RealtimePayload<T>) => void,
): { unsubscribe: UnsubscribeFn } {
  console.log(`[Realtime Mock] Subscription created for ${table} - No backend connected`);

  const unsubscribe = () => {
    console.log(`[Realtime Mock] Unsubscribing from ${table}`);
  };

  return { unsubscribe };
}

// ============================================
// Inference Jobs Subscription
// ============================================

export function subscribeToJobs(
  callback: (payload: RealtimePayload<InferenceJob>) => void,
  // eslint-disable-next-line @typescript-eslint/no-unused-vars, @typescript-eslint/no-explicit-any
  options: any = {},
): UnsubscribeFn {
  const { unsubscribe } = createMockSubscription<InferenceJob>("inference_jobs", callback);
  return unsubscribe;
}

export function subscribeToJob(
  jobId: string,
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  callback: (job: InferenceJob) => void,
): UnsubscribeFn {
  console.log(`[Realtime Mock] Subscribed to job ${jobId}`);
  return () => {
    console.log(`[Realtime Mock] Unsubscribing from job ${jobId}`);
  };
}

// ============================================
// Performance Metrics Subscription
// ============================================

export function subscribeToMetrics(
  callback: (payload: RealtimePayload<PerformanceMetric>) => void,
  // eslint-disable-next-line @typescript-eslint/no-unused-vars, @typescript-eslint/no-explicit-any
  options: any = {},
): UnsubscribeFn {
  const { unsubscribe } = createMockSubscription<PerformanceMetric>(
    "performance_metrics",
    callback,
  );
  return unsubscribe;
}

export function subscribeToJobMetrics(
  jobId: string,
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  callback: (metric: PerformanceMetric) => void,
): UnsubscribeFn {
  console.log(`[Realtime Mock] Subscribed to metrics for job ${jobId}`);
  return () => {
    console.log(`[Realtime Mock] Unsubscribing from metrics for job ${jobId}`);
  };
}

// ============================================
// Alerts Subscription
// ============================================

export function subscribeToAlerts(
  callback: (payload: RealtimePayload<Alert>) => void,
  // eslint-disable-next-line @typescript-eslint/no-unused-vars, @typescript-eslint/no-explicit-any
  options: any = {},
): UnsubscribeFn {
  const { unsubscribe } = createMockSubscription<Alert>("alerts", callback);
  return unsubscribe;
}

export function subscribeToNewAlerts(callback: (alert: Alert) => void): UnsubscribeFn {
  return subscribeToAlerts((payload) => {
    if (payload.eventType === "INSERT") {
      callback(payload.new);
    }
  });
}

// ============================================
// Module Status Subscription
// ============================================

export function subscribeToModuleStatus(
  callback: (payload: RealtimePayload<ModuleStatus>) => void,
  // eslint-disable-next-line @typescript-eslint/no-unused-vars, @typescript-eslint/no-explicit-any
  options: any = {},
): UnsubscribeFn {
  const { unsubscribe } = createMockSubscription<ModuleStatus>("module_status", callback);
  return unsubscribe;
}

export function subscribeToModuleByName(
  moduleName: string,
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  callback: (status: ModuleStatus) => void,
): UnsubscribeFn {
  console.log(`[Realtime Mock] Subscribed to module ${moduleName}`);
  return () => {
    console.log(`[Realtime Mock] Unsubscribing from module ${moduleName}`);
  };
}

// ============================================
// System Metrics Subscription
// ============================================

export function subscribeToSystemMetrics(
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  callback: (payload: RealtimePayload<SystemMetrics>) => void,
): UnsubscribeFn {
  console.log(`[Realtime Mock] Subscribed to system metrics`);
  return () => {
    console.log(`[Realtime Mock] Unsubscribing from system metrics`);
  };
}

// ============================================
// Combined Subscriptions
// ============================================

export function subscribeToDashboard(callbacks: {
  onJobChange?: (payload: RealtimePayload<InferenceJob>) => void;
  onMetricChange?: (payload: RealtimePayload<PerformanceMetric>) => void;
  onAlertChange?: (payload: RealtimePayload<Alert>) => void;
  onModuleStatusChange?: (payload: RealtimePayload<ModuleStatus>) => void;
}): UnsubscribeFn {
  const unsubscribers: UnsubscribeFn[] = [];

  if (callbacks.onJobChange) unsubscribers.push(subscribeToJobs(callbacks.onJobChange));
  if (callbacks.onMetricChange) unsubscribers.push(subscribeToMetrics(callbacks.onMetricChange));
  if (callbacks.onAlertChange) unsubscribers.push(subscribeToAlerts(callbacks.onAlertChange));
  if (callbacks.onModuleStatusChange)
    unsubscribers.push(subscribeToModuleStatus(callbacks.onModuleStatusChange));

  return () => {
    console.log("[Realtime Mock] Cleaning up all dashboard subscriptions");
    unsubscribers.forEach((unsub) => unsub());
  };
}
