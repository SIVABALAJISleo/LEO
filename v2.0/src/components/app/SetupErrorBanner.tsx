import { useEffect, useState } from "react";
import { AlertTriangle, X } from "lucide-react";
import { validateEnv, type EnvIssue } from "@/lib/env-check";

export function SetupErrorBanner() {
  const [issues, setIssues] = useState<EnvIssue[]>([]);
  const [dismissed, setDismissed] = useState(false);

  useEffect(() => {
    setIssues(validateEnv());
    const onStorage = () => setIssues(validateEnv());
    window.addEventListener("storage", onStorage);
    return () => window.removeEventListener("storage", onStorage);
  }, []);

  const errors = issues.filter((i) => i.severity === "error");
  const warnings = issues.filter((i) => i.severity === "warning");
  if (dismissed || (errors.length === 0 && warnings.length === 0)) return null;
  const hasErrors = errors.length > 0;

  return (
    <div
      role="alert"
      aria-live="assertive"
      className={`border-b ${hasErrors ? "bg-destructive/10 border-destructive/40" : "bg-yellow-500/10 border-yellow-500/40"}`}
    >
      <div className="mx-auto flex max-w-[1440px] items-start gap-3 px-6 py-3 text-sm">
        <AlertTriangle className="h-5 w-5 shrink-0 mt-0.5 text-leo" aria-hidden />
        <div className="flex-1 min-w-0">
          <div className="font-display font-bold">
            {hasErrors ? "Setup error — LEO backend not configured" : "Configuration warning"}
          </div>
          <ul className="mt-1 space-y-1 text-muted-foreground">
            {[...errors, ...warnings].map((i) => (
              <li key={i.key}>
                <span className="font-mono text-xs text-foreground">{i.key}</span> — {i.message}
              </li>
            ))}
          </ul>
          <a
            href="/app/settings"
            className="mt-2 inline-block text-xs font-semibold text-leo hover:underline focus:outline-none focus-visible:ring-2 focus-visible:ring-leo"
          >
            Open Settings ›
          </a>
        </div>
        <button
          onClick={() => setDismissed(true)}
          aria-label="Dismiss"
          className="p-1 hover:text-leo focus:outline-none focus-visible:ring-2 focus-visible:ring-leo"
        >
          <X className="h-4 w-4" />
        </button>
      </div>
    </div>
  );
}
