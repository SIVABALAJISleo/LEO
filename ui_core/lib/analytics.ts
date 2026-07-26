import { firebaseClient as supabase } from "@/integrations/firebase/client";

export type AnalyticsEventType =
  | "page_view"
  | "job_created"
  | "job_completed"
  | "job_failed"
  | "module_config_changed"
  | "api_key_created"
  | "api_key_revoked"
  | "export_data"
  | "login"
  | "signup"
  | "logout";

interface AnalyticsEvent {
  eventType: AnalyticsEventType;
  pagePath?: string;
  eventData?: Record<string, unknown>;
}

/**
 * Track an analytics event
 */
export async function trackEvent(event: AnalyticsEvent): Promise<void> {
  const { eventType, pagePath, eventData = {} } = event;

  try {
    const {
      data: { user },
    } = await supabase.auth.getUser();

    const insertData: Record<string, unknown> = {
      event_type: eventType,
      page_path: pagePath || (typeof window !== "undefined" ? window.location.pathname : null),
      event_data: eventData,
    };

    if (user?.id) {
      insertData.user_id = user.id;
    }

    const { error } = await supabase.from("analytics_events").insert(insertData as never);

    if (error) {
      console.error("Failed to track event:", error);
    }
  } catch (e) {
    // Silent fail for analytics - don't break the user experience
    console.error("Analytics tracking failed:", e);
  }
}

/**
 * Track a page view
 */
export function trackPageView(pagePath?: string): void {
  trackEvent({
    eventType: "page_view",
    pagePath: pagePath || window.location.pathname,
  });
}

/**
 * Track job creation
 */
export function trackJobCreated(jobId: string, modelId: string): void {
  trackEvent({
    eventType: "job_created",
    eventData: { jobId, modelId },
  });
}

/**
 * Track job completion
 */
export function trackJobCompleted(jobId: string, durationMs: number): void {
  trackEvent({
    eventType: "job_completed",
    eventData: { jobId, durationMs },
  });
}

/**
 * Track job failure
 */
export function trackJobFailed(jobId: string, errorMessage: string): void {
  trackEvent({
    eventType: "job_failed",
    eventData: { jobId, errorMessage },
  });
}

/**
 * Track module config change
 */
export function trackModuleConfigChanged(moduleName: string, enabled: boolean): void {
  trackEvent({
    eventType: "module_config_changed",
    eventData: { moduleName, enabled },
  });
}

/**
 * Create analytics hook for React components
 */
export function useAnalytics() {
  return {
    trackEvent,
    trackPageView,
    trackJobCreated,
    trackJobCompleted,
    trackJobFailed,
    trackModuleConfigChanged,
  };
}
