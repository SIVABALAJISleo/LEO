// Timeline of health degradation alert episodes with time-range filtering.
import { useMemo, useState } from "react";
import { toast } from "sonner";
import { useAlertTimeline, clearAlertTimeline, type AlertEvent } from "@/lib/health-alert-timeline";

type Range = "1h" | "24h" | "7d" | "all";

const RANGE_MS: Record<Range, number | null> = {
  "1h": 60 * 60_000,
  "24h": 24 * 60 * 60_000,
  "7d": 7 * 24 * 60 * 60_000,
  all: null,
};

function fmtTime(ts: number) {
  return new Date(ts).toLocaleString();
}

function fmtDuration(ms: number) {
  if (ms < 1000) return `${ms}ms`;
  const s = Math.round(ms / 1000);
  if (s < 60) return `${s}s`;
  const m = Math.floor(s / 60);
  const rs = s % 60;
  if (m < 60) return rs ? `${m}m ${rs}s` : `${m}m`;
  const h = Math.floor(m / 60);
  const rm = m % 60;
  return rm ? `${h}h ${rm}m` : `${h}h`;
}

type LevelFilter = "all" | "warn" | "critical";

export function HealthAlertTimeline() {
  const events = useAlertTimeline();
  const [range, setRange] = useState<Range>("24h");
  const [level, setLevel] = useState<LevelFilter>("all");
  const [query, setQuery] = useState("");

  const filtered = useMemo(() => {
    const cutoff = RANGE_MS[range];
    const now = Date.now();
    const q = query.trim().toLowerCase();
    const list = events.filter((e) => {
      if (cutoff !== null && (e.endedAt ?? now) < now - cutoff) return false;
      if (level !== "all" && e.peakLevel !== level) return false;
      if (q) {
        const reasons = [...e.startReasons, ...e.lastReasons].join(" ").toLowerCase();
        if (!reasons.includes(q)) return false;
      }
      return true;
    });
    return list.slice().reverse();
  }, [events, range, level, query]);

  return (
    <div className="border border-border p-4">
      <div className="flex flex-wrap items-baseline justify-between gap-2">
        <div>
          <p className="eyebrow">Alert timeline</p>
          <p className="mt-1 text-xs text-muted-foreground">
            Every warn/critical episode with start, end, and thresholds exceeded.
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <fieldset className="flex gap-1" aria-label="Filter timeline by time range">
            {(Object.keys(RANGE_MS) as Range[]).map((r) => (
              <button
                key={r}
                type="button"
                onClick={() => setRange(r)}
                aria-pressed={range === r}
                className={
                  "border px-2 py-0.5 text-[11px] font-semibold focus:outline-none focus-visible:ring-2 focus-visible:ring-leo " +
                  (range === r
                    ? "border-leo bg-leo/10 text-leo"
                    : "border-border hover:border-leo hover:text-leo")
                }
              >
                {r === "all" ? "All" : r}
              </button>
            ))}
          </fieldset>
          <button
            type="button"
            onClick={() => {
              clearAlertTimeline();
              toast.success("Alert timeline cleared");
            }}
            className="border border-border px-2 py-0.5 text-[11px] font-semibold hover:border-red-500 hover:text-red-400 focus:outline-none focus-visible:ring-2 focus-visible:ring-red-500"
          >
            Clear
          </button>
        </div>
      </div>

      <div className="mt-3 flex flex-wrap items-center gap-2">
        <fieldset className="flex gap-1" aria-label="Filter timeline by level">
          {(["all", "warn", "critical"] as LevelFilter[]).map((l) => {
            const active = level === l;
            const tone =
              l === "critical"
                ? active
                  ? "border-red-500 bg-red-500/10 text-red-300"
                  : "hover:border-red-500 hover:text-red-400"
                : l === "warn"
                  ? active
                    ? "border-yellow-400 bg-yellow-400/10 text-yellow-200"
                    : "hover:border-yellow-400 hover:text-yellow-200"
                  : active
                    ? "border-leo bg-leo/10 text-leo"
                    : "hover:border-leo hover:text-leo";
            return (
              <button
                key={l}
                type="button"
                onClick={() => setLevel(l)}
                aria-pressed={active}
                className={`border border-border px-2 py-0.5 text-[11px] font-semibold uppercase focus:outline-none focus-visible:ring-2 focus-visible:ring-leo ${tone}`}
              >
                {l}
              </button>
            );
          })}
        </fieldset>
        <label className="flex flex-1 min-w-[180px] items-center gap-2 text-xs">
          <span className="sr-only">Search alert reasons</span>
          <input
            type="search"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search reasons (e.g. latency, 500, cors)…"
            className="w-full border border-border bg-background px-2 py-1 font-mono text-xs focus:border-leo focus:outline-none"
          />
        </label>
        <span className="text-[11px] text-muted-foreground">
          {filtered.length}/{events.length}
        </span>
      </div>

      {filtered.length === 0 ? (
        <p className="mt-4 text-xs text-muted-foreground">
          No alerts match these filters. Try widening the range or clearing the search.
        </p>
      ) : (
        <ul className="mt-4 space-y-2" aria-live="polite">
          {filtered.map((e) => (
            <TimelineRow key={e.id} event={e} />
          ))}
        </ul>
      )}
    </div>
  );
}

function TimelineRow({ event }: { event: AlertEvent }) {
  const ended = event.endedAt ?? null;
  const duration = ended ? ended - event.startedAt : Date.now() - event.startedAt;
  const isCritical = event.peakLevel === "critical";
  return (
    <li
      className={
        "border-l-2 p-2 text-xs " +
        (isCritical ? "border-red-500 bg-red-500/5" : "border-yellow-500 bg-yellow-500/5")
      }
    >
      <div className="flex flex-wrap items-baseline justify-between gap-2">
        <p
          className={
            "font-semibold uppercase tracking-wide " +
            (isCritical ? "text-red-400" : "text-yellow-200")
          }
        >
          {isCritical ? "Critical" : "Warn"}
          {ended ? "" : " · ongoing"}
        </p>
        <p className="font-mono text-[11px] text-muted-foreground">{fmtDuration(duration)}</p>
      </div>
      <p className="mt-1 text-[11px] text-muted-foreground">
        {fmtTime(event.startedAt)} → {ended ? fmtTime(ended) : "now"}
      </p>
      <ul className="mt-1 list-inside list-disc space-y-0.5">
        {(event.lastReasons.length ? event.lastReasons : event.startReasons).map((r) => (
          <li key={r}>{r}</li>
        ))}
      </ul>
    </li>
  );
}
