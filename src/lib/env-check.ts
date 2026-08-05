// Runtime validation for required environment configuration.
// Runs on the client at app startup. Returns a list of problems so the UI
// can show a clear setup error instead of a broken app.

export type EnvIssue = {
  key: string;
  message: string;
  severity: "error" | "warning";
};

const URL_RE = /^https?:\/\/[^\s/$.?#].[^\s]*$/i;

export function validateEnv(): EnvIssue[] {
  const issues: EnvIssue[] = [];
  const base =
    (typeof window !== "undefined" && window.localStorage.getItem("leo.api_base")) ||
    (import.meta.env.VITE_LEO_API_BASE_URL as string | undefined) ||
    "http://localhost:8005/api/v1";

  if (!base || !base.trim()) {
    issues.push({
      key: "VITE_LEO_API_BASE_URL",
      severity: "error",
      message:
        "No LEO backend URL is configured. Set VITE_LEO_API_BASE_URL in your .env or configure it in Settings.",
    });
  } else if (!URL_RE.test(base.trim())) {
    issues.push({
      key: "VITE_LEO_API_BASE_URL",
      severity: "error",
      message: `Invalid backend URL: "${base}". Must be an http(s) URL (e.g. http://localhost:8000).`,
    });
  } else if (
    typeof window !== "undefined" &&
    window.location.protocol === "https:" &&
    base.startsWith("http://") &&
    !/^http:\/\/(localhost|127\.0\.0\.1)/i.test(base)
  ) {
    issues.push({
      key: "VITE_LEO_API_BASE_URL",
      severity: "warning",
      message:
        "Frontend is on HTTPS but backend URL is HTTP. Browsers will block requests as mixed content.",
    });
  }

  return issues;
}
