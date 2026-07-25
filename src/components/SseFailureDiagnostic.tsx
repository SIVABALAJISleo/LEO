// SSE failure diagnostic: inspects persisted SSE diagnostics + recent health
// history to guess the most likely root cause (CORS, network, wrong base URL,
// tunnel unreachable) and shows the exact next steps.
import { useEffect, useState } from "react";
import { Link, useNavigate } from "@tanstack/react-router";
import { toast } from "sonner";
import { getApiBase, getApiBaseSource } from "@/lib/leo-client";
import { useHealthHistory } from "@/lib/health-history";

const DIAG_KEY = "leo.bench.sse-diag";

type PersistedDiag = {
  lastEventAt: number | null;
  lastError: string | null;
  reconnectAttempts: number;
  transport: "sse" | "polling";
  status: "idle" | "open" | "reconnecting" | "closed" | "error" | "polling";
  savedAt: number;
};

type Cause = {
  id: "cors" | "network" | "wrong-base" | "tunnel" | "mixed-content" | "healthy" | "idle";
  title: string;
  confidence: "high" | "medium" | "low";
  why: string[];
  fix: { text: string; href?: string }[];
};

function readDiag(): PersistedDiag | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = window.localStorage.getItem(DIAG_KEY);
    return raw ? (JSON.parse(raw) as PersistedDiag) : null;
  } catch {
    return null;
  }
}

function diagnose(
  diag: PersistedDiag | null,
  base: string,
  recentFailures: number,
  recentCorsHint: boolean,
  recentMixedContent: boolean,
  everOnline: boolean,
): Cause {
  const pageHttps = typeof window !== "undefined" && window.location.protocol === "https:";
  const baseHttp = base.startsWith("http://");
  const isLocal = /localhost|127\.0\.0\.1|0\.0\.0\.0/.test(base);
  const err = (diag?.lastError ?? "").toLowerCase();

  if (!diag || diag.status === "idle") {
    return {
      id: "idle",
      title: "No SSE session yet",
      confidence: "low",
      why: ["Start a benchmark run to open the EventSource stream."],
      fix: [{ text: "Open Benchmark runner", href: "/benchmarks" }],
    };
  }

  if (diag.status === "open" && recentFailures === 0) {
    return {
      id: "healthy",
      title: "Stream healthy",
      confidence: "high",
      why: ["EventSource is open and health checks are passing."],
      fix: [],
    };
  }

  if (pageHttps && baseHttp) {
    return {
      id: "mixed-content",
      title: "Mixed content blocked",
      confidence: "high",
      why: [
        "Page is https but VITE_LEO_API_BASE_URL is http.",
        "Browsers silently block EventSource across this boundary.",
      ],
      fix: [
        { text: "Use an https tunnel URL (Cloudflare Tunnel or ngrok)" },
        { text: "Update base URL in Settings", href: "/app/settings" },
      ],
    };
  }

  if (recentCorsHint || err.includes("cors") || err.includes("access-control")) {
    return {
      id: "cors",
      title: "CORS blocking the stream",
      confidence: "high",
      why: [
        "Recent health checks or SSE errors mention CORS.",
        "EventSource requires Access-Control-Allow-Origin on the SSE response.",
      ],
      fix: [
        { text: "Run the CORS preflight tester below and copy the curl output" },
        {
          text: "Add CORSMiddleware(allow_origins=[…], allow_methods=['*']) to FastAPI",
        },
      ],
    };
  }

  if (recentMixedContent) {
    return {
      id: "mixed-content",
      title: "Mixed content blocked",
      confidence: "high",
      why: ["Health checks flagged mixed-content."],
      fix: [{ text: "Serve the backend over https" }],
    };
  }

  if (
    !everOnline &&
    isLocal &&
    typeof window !== "undefined" &&
    window.location.hostname !== "localhost"
  ) {
    return {
      id: "tunnel",
      title: "Localhost base URL not reachable from this origin",
      confidence: "high",
      why: [
        `Base URL "${base}" points at localhost but this app is served from ${window.location.hostname}.`,
        "The preview environment cannot reach your laptop directly.",
      ],
      fix: [
        { text: "Start a Cloudflare Tunnel or ngrok tunnel to your backend" },
        { text: "Paste the public tunnel URL into Settings", href: "/app/settings" },
      ],
    };
  }

  if (!everOnline && recentFailures > 0) {
    return {
      id: "wrong-base",
      title: "Base URL never responded successfully",
      confidence: "medium",
      why: [
        `No successful /health response from "${base}".`,
        "DNS resolves but the endpoint returns nothing usable, or the path is wrong.",
      ],
      fix: [
        { text: "Verify the URL and port match your running backend" },
        { text: "Reset to defaults in the Backend health panel" },
      ],
    };
  }

  return {
    id: "network",
    title: "Transient network / server issue",
    confidence: recentFailures > 3 ? "medium" : "low",
    why: [
      `Reconnect attempts: ${diag.reconnectAttempts}.`,
      diag.lastError ? `Last error: ${diag.lastError}` : "Connection drops without a clear error.",
    ],
    fix: [
      { text: "Check backend logs for crashes or timeouts" },
      { text: "Use the manual Re-run checks button to resample" },
    ],
  };
}

export function SseFailureDiagnostic() {
  const history = useHealthHistory();
  const [diag, setDiag] = useState<PersistedDiag | null>(() => readDiag());
  const navigate = useNavigate();

  useEffect(() => {
    const id = setInterval(() => setDiag(readDiag()), 2000);
    return () => clearInterval(id);
  }, []);

  async function copyAndConfigure() {
    const suggestion = [
      `# LEO effective API base URL`,
      `VITE_LEO_API_BASE_URL=${getApiBase()}`,
      ``,
      `# Recommended update:`,
      `# 1. Replace with your public backend URL (https:// tunnel if page is https).`,
      `# 2. Save in Settings — the new value will override any env default.`,
    ].join("\n");
    try {
      await navigator.clipboard.writeText(suggestion);
      toast.success("Copied API base + settings hint");
    } catch {
      toast.error("Clipboard blocked — opening Settings anyway");
    }
    navigate({
      to: "/app/settings",
      search: { apiBase: getApiBase() } as never,
    });
  }

  const base = getApiBase();
  const source = getApiBaseSource();
  const recent = history.slice(-10);
  const recentFailures = recent.filter((e) => e.status !== "online").length;
  const recentCorsHint = recent.some((e) => e.failureKind === "cors");
  const recentMixedContent = recent.some((e) => e.failureKind === "mixed-content");
  const everOnline = history.some((e) => e.status === "online");

  const cause = diagnose(
    diag,
    base,
    recentFailures,
    recentCorsHint,
    recentMixedContent,
    everOnline,
  );

  const tone =
    cause.id === "healthy"
      ? "border-leo/40"
      : cause.id === "idle"
        ? "border-border"
        : "border-yellow-500/50";

  return (
    <div className={`border-l-2 ${tone} p-4`}>
      <div className="flex flex-wrap items-baseline justify-between gap-2">
        <p className="eyebrow">SSE failure diagnostic</p>
        <span className="text-[10px] uppercase tracking-wide text-muted-foreground">
          confidence: {cause.confidence}
        </span>
      </div>
      <p className="mt-2 text-sm font-semibold">{cause.title}</p>

      {cause.why.length > 0 && (
        <ul className="mt-2 space-y-1 text-xs text-muted-foreground">
          {cause.why.map((w) => (
            <li key={w}>• {w}</li>
          ))}
        </ul>
      )}

      {cause.fix.length > 0 && (
        <div className="mt-3">
          <p className="text-[11px] font-semibold uppercase tracking-wide text-muted-foreground">
            Next steps
          </p>
          <ol className="mt-1 space-y-1 text-xs">
            {cause.fix.map((f, i) => (
              <li key={i}>
                {i + 1}.{" "}
                {f.href ? (
                  <Link
                    to={f.href}
                    className="text-leo underline underline-offset-2 hover:text-leo/80"
                  >
                    {f.text}
                  </Link>
                ) : (
                  f.text
                )}
              </li>
            ))}
          </ol>
        </div>
      )}

      <div className="mt-3 flex flex-wrap items-center justify-between gap-2">
        <p className="text-[10px] text-muted-foreground">
          base: <code className="font-mono">{base}</code> · source: {source}
        </p>
        <button
          type="button"
          onClick={copyAndConfigure}
          className="border border-leo bg-leo/10 px-3 py-1 text-[11px] font-semibold text-leo hover:bg-leo/20 focus:outline-none focus-visible:ring-2 focus-visible:ring-leo"
        >
          Copy URL & configure ›
        </button>
      </div>
    </div>
  );
}
