// Generate ready-to-paste backend CORS configuration snippets from the last
// CORS preflight run stored by CorsPreflightTester. Supports Express, NestJS,
// FastAPI, Vite proxy, and a generic header list.
import { useEffect, useState } from "react";
import { toast } from "sonner";

interface PreflightSnapshot {
  url: string;
  origin: string;
  method: string;
  ok: boolean;
  checks: {
    header: string;
    received: string | null;
    kind: "ok" | "warn" | "fail";
    note?: string;
  }[];
  rawHeaders: [string, string][];
}

const KEY = "leo.cors.last_result";

function readSnapshot(): PreflightSnapshot | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = window.localStorage.getItem(KEY);
    return raw ? (JSON.parse(raw) as PreflightSnapshot) : null;
  } catch {
    return null;
  }
}

type Framework = "express" | "nest" | "fastapi" | "vite" | "generic";

interface Config {
  origin: string;
  methods: string[];
  headers: string[];
}

function deriveConfig(snap: PreflightSnapshot): Config {
  // Prefer union of received Allow-* headers + what the request actually
  // needed, so failing checks get patched.
  const received = new Map(snap.rawHeaders.map(([k, v]) => [k.toLowerCase(), v]));
  const parseList = (v: string | undefined | null) =>
    (v ?? "")
      .split(/[,\s]+/)
      .map((s) => s.trim())
      .filter(Boolean);

  const methodsRecv = parseList(received.get("access-control-allow-methods"));
  const headersRecv = parseList(received.get("access-control-allow-headers"));

  const methods = Array.from(
    new Set([...methodsRecv, snap.method, "GET", "POST", "OPTIONS"].map((m) => m.toUpperCase())),
  ).filter((m) => m !== "*");

  const requested = snap.checks
    .filter((c) => c.header === "Access-Control-Allow-Headers")
    .flatMap((c) => {
      const missing = (c.note ?? "").match(/Missing:\s*(.*)$/i)?.[1];
      return missing ? missing.split(/,\s*/) : [];
    });

  const headers = Array.from(
    new Set([...headersRecv, ...requested, "Content-Type", "Authorization"].map((h) => h.trim())),
  ).filter((h) => h && h !== "*");

  return { origin: snap.origin, methods, headers };
}

function snippet(fw: Framework, cfg: Config): string {
  const originJson = JSON.stringify(cfg.origin);
  const methodsJson = JSON.stringify(cfg.methods);
  const headersJson = JSON.stringify(cfg.headers);
  const headersCsv = cfg.headers.join(", ");
  const methodsCsv = cfg.methods.join(", ");

  switch (fw) {
    case "express":
      return `import cors from "cors";

app.use(cors({
  origin: ${originJson},
  methods: ${methodsJson},
  allowedHeaders: ${headersJson},
  credentials: false,
  maxAge: 86400,
}));

// Ensure OPTIONS preflight succeeds for every route:
app.options("*", cors());`;

    case "nest":
      return `// main.ts
app.enableCors({
  origin: ${originJson},
  methods: ${methodsJson},
  allowedHeaders: ${headersJson},
  credentials: false,
  maxAge: 86400,
});`;

    case "fastapi":
      return `from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[${originJson}],
    allow_methods=${JSON.stringify(cfg.methods)},
    allow_headers=${JSON.stringify(cfg.headers)},
    allow_credentials=False,
    max_age=86400,
)`;

    case "vite":
      return `// vite.config.ts — proxy the frontend dev server to your backend
// so the browser never sees a cross-origin request in dev.
export default defineConfig({
  server: {
    proxy: {
      "/api": {
        target: "http://localhost:8005",
        changeOrigin: true,
        secure: false,
      },
      "/health": {
        target: "http://localhost:8005",
        changeOrigin: true,
        secure: false,
      },
    },
  },
});`;

    case "generic":
      return `# Response headers your backend MUST send on every response
# (and on the OPTIONS preflight):

Access-Control-Allow-Origin: ${cfg.origin}
Access-Control-Allow-Methods: ${methodsCsv}
Access-Control-Allow-Headers: ${headersCsv}
Access-Control-Max-Age: 86400

# Preflight (OPTIONS) must return 204 with the headers above.`;
  }
}

const TABS: { id: Framework; label: string }[] = [
  { id: "express", label: "Express" },
  { id: "nest", label: "NestJS" },
  { id: "fastapi", label: "FastAPI" },
  { id: "vite", label: "Vite proxy" },
  { id: "generic", label: "Generic" },
];

export function CorsSnippetsPanel() {
  const [snap, setSnap] = useState<PreflightSnapshot | null>(() => readSnapshot());
  const [tab, setTab] = useState<Framework>("fastapi");

  useEffect(() => {
    const handler = () => setSnap(readSnapshot());
    window.addEventListener("storage", handler);
    // Poll every 2s so it updates after a fresh preflight in the same tab.
    const id = setInterval(handler, 2000);
    return () => {
      window.removeEventListener("storage", handler);
      clearInterval(id);
    };
  }, []);

  if (!snap) {
    return (
      <div className="border border-border p-4">
        <p className="eyebrow">Backend CORS snippets</p>
        <p className="mt-2 text-xs text-muted-foreground">
          Run a preflight above first — the exact allow-headers, methods, and origin will be filled
          in here.
        </p>
      </div>
    );
  }

  const cfg = deriveConfig(snap);
  const code = snippet(tab, cfg);

  async function copy() {
    try {
      await navigator.clipboard.writeText(code);
      toast.success(`${TABS.find((t) => t.id === tab)?.label} snippet copied`);
    } catch {
      toast.error("Clipboard blocked — select and copy manually");
    }
  }

  return (
    <div className="border border-border p-4">
      <div className="flex flex-wrap items-baseline justify-between gap-2">
        <div>
          <p className="eyebrow">Backend CORS snippets</p>
          <p className="mt-1 text-xs text-muted-foreground">
            Generated from your last preflight ({snap.method} {snap.url}).
          </p>
        </div>
        <button
          type="button"
          onClick={copy}
          className="border border-border px-3 py-1 text-[11px] font-semibold hover:border-leo hover:text-leo focus:outline-none focus-visible:ring-2 focus-visible:ring-leo"
        >
          Copy snippet
        </button>
      </div>

      <div role="tablist" aria-label="Framework" className="mt-3 flex flex-wrap gap-1">
        {TABS.map((t) => (
          <button
            key={t.id}
            role="tab"
            aria-selected={tab === t.id}
            type="button"
            onClick={() => setTab(t.id)}
            className={
              "border px-2 py-0.5 text-[11px] font-semibold focus:outline-none focus-visible:ring-2 focus-visible:ring-leo " +
              (tab === t.id
                ? "border-leo bg-leo/10 text-leo"
                : "border-border hover:border-leo hover:text-leo")
            }
          >
            {t.label}
          </button>
        ))}
      </div>

      <div className="mt-3 grid gap-1 text-[11px] text-muted-foreground sm:grid-cols-3">
        <span>
          origin: <code className="font-mono text-foreground">{cfg.origin}</code>
        </span>
        <span>
          methods: <code className="font-mono text-foreground">{cfg.methods.join(", ")}</code>
        </span>
        <span>
          headers: <code className="font-mono text-foreground">{cfg.headers.join(", ")}</code>
        </span>
      </div>

      <pre className="mt-3 overflow-x-auto bg-input p-3 font-mono text-[11px] whitespace-pre">
        {code}
      </pre>
    </div>
  );
}
