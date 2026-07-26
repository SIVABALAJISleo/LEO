/**
 * src/services/analytics/QuantumAnalytics.ts
 * Telemetry & Analytics Tracking
 */
export class QuantumAnalytics {
  private endpoint: string;

  constructor(endpoint: string = "/api/v1/telemetry") {
    this.endpoint = endpoint;
  }

  public track(event: string, properties: Record<string, any> = {}) {
    const payload = {
      event,
      properties: {
        ...properties,
        timestamp: new Date().toISOString(),
        url: typeof window !== "undefined" ? window.location.href : "",
        userAgent: typeof navigator !== "undefined" ? navigator.userAgent : "",
      },
    };

    if (process.env.NODE_ENV === "production" && typeof fetch !== "undefined") {
      fetch(this.endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      }).catch((err) => {
        console.warn("[LEO Analytics] Telemetry log buffered locally:", err);
      });
    } else {
      console.log("[LEO Quantum Analytics]", event, properties);
    }
  }

  public page(name: string, properties: Record<string, any> = {}) {
    this.track("page_viewed", { page_name: name, ...properties });
  }
}

export const quantumAnalytics = new QuantumAnalytics();
