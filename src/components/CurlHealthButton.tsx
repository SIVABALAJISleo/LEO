import { useState } from "react";
import { toast } from "sonner";
import { buildHealthUrl } from "@/lib/backend-health";
import { getApiBase } from "@/lib/leo-client";

interface Props {
  label: string;
  path: string; // e.g. "/health" or "/api/v1/leo/metrics"
  extra?: string; // extra curl flags
}

function CurlBlock({ label, path, extra = "" }: Props) {
  const [open, setOpen] = useState(false);
  const url = path === "/health" ? buildHealthUrl() : `${getApiBase().replace(/\/+$/, "")}${path}`;
  const cmd = `curl -sS ${extra} -w '\\nHTTP %{http_code} · %{time_total}s\\n' -o - '${url}'`
    .replace(/\s+/g, " ")
    .trim();

  async function copy() {
    try {
      await navigator.clipboard.writeText(cmd);
      toast.success("curl command copied to clipboard");
    } catch {
      toast.error("Clipboard blocked — select and copy manually");
    }
  }

  return (
    <div className="inline-flex flex-col items-start gap-2">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        className="border border-border px-3 py-1.5 text-xs font-medium hover:border-leo hover:text-leo focus:outline-none focus-visible:ring-2 focus-visible:ring-leo"
        aria-expanded={open}
      >
        {open ? `Hide curl (${label})` : `Generate curl for ${label}`}
      </button>
      {open && (
        <div className="w-full max-w-2xl border border-border bg-background/80 p-3">
          <div className="mb-2 text-[11px] text-muted-foreground">
            Run this from your laptop or tunnel host to test the exact URL the frontend calls:
          </div>
          <pre className="overflow-auto whitespace-pre-wrap break-all rounded bg-black/40 p-3 font-mono text-[11px] text-leo">
            {cmd}
          </pre>
          <div className="mt-2 flex gap-2">
            <button
              type="button"
              onClick={copy}
              className="border border-border px-3 py-1 text-[11px] hover:border-leo hover:text-leo"
            >
              Copy
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export function CurlHealthButton() {
  return <CurlBlock label="/health" path="/health" />;
}

export function CurlMetricsButton() {
  return (
    <CurlBlock
      label="/api/v1/leo/metrics"
      path="/api/v1/leo/metrics"
      extra="-H 'Accept: application/json'"
    />
  );
}
