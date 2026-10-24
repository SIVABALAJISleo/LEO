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
    <div className="relative overflow-hidden rounded-2xl border border-border/60 bg-card/60 p-5 shadow-lg backdrop-blur-xl">
      <div className="flex flex-wrap items-baseline justify-between gap-2">
        <div>
          <p className="text-xs font-bold uppercase tracking-wider text-muted-foreground">
            Alert timeline
          </p>
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
                  "rounded-lg border px-2.5 py-1 text-xs font-semibold transition-all focus:outline-none focus-visible:ring-2 focus-visible:ring-primary " +
                  (range === r
                    ? "border-primary bg-primary/20 text-primary"
                    : "border-border/60 bg-muted/20 text-muted-foreground hover:border-primary/40 hover:text-foreground")
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
            className="rounded-lg border border-border/60 bg-muted/20 px-2.5 py-1 text-xs font-semibold text-muted-foreground hover:border-red-500/60 hover:text-red-400 focus:outline-none transition-all"
          >
            Clear
          </button>
        </div>
      </div>

      <div className="mt-3 flex flex-wrap items-center gap-2">
        <fieldset className="flex gap-1" aria-label="Filter timeline by level">
          {(["all", "warn", "critical"] as LevelFilter[]).map((l) => {
            const active = level === l;
            return (
              <button
                key={l}
                type="button"
                onClick={() => setLevel(l)}
                aria-pressed={active}
                className={
                  "rounded-lg border px-2.5 py-1 text-xs font-semibold capitalize transition-all focus:outline-none " +
                  (active
                    ? l === "critical"
                      ? "border-red-500/60 bg-red-500/20 text-red-300"
                      : l === "warn"
                        ? "border-amber-500/60 bg-amber-500/20 text-amber-300"
                        : "border-primary bg-primary/20 text-primary"
                    : "border-border/60 bg-muted/20 text-muted-foreground hover:border-primary/40 hover:text-foreground")
                }
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
            className="w-full rounded-lg border border-border/60 bg-background/50 px-3 py-1 font-mono text-xs focus:border-primary focus:outline-none text-foreground"
          />
        </label>
        <span className="text-[11px] text-muted-foreground font-mono">
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
        "rounded-xl border p-3 text-xs transition-all " +
        (isCritical
          ? "border-red-500/30 bg-red-950/20 text-red-200"
          : "border-amber-500/30 bg-amber-950/20 text-amber-200")
      }
    >
      <div className="flex flex-wrap items-baseline justify-between gap-2">
        <p
          className={
            "font-semibold uppercase tracking-wider text-[11px] flex items-center gap-2 " +
            (isCritical ? "text-red-400" : "text-amber-300")
          }
        >
          <span
            className={"h-2 w-2 rounded-full " + (isCritical ? "bg-red-500" : "bg-amber-400")}
          />
          {isCritical ? "Critical" : "Warn"}
          {ended ? "" : " · ongoing"}
        </p>
        <p className="font-mono text-[11px] text-muted-foreground">{fmtDuration(duration)}</p>
      </div>
      <p className="mt-1 text-[11px] text-muted-foreground font-mono">
        {fmtTime(event.startedAt)} → {ended ? fmtTime(ended) : "now"}
      </p>
      <ul className="mt-1.5 list-inside list-disc space-y-0.5 text-muted-foreground">
        {(event.lastReasons.length ? event.lastReasons : event.startReasons).map((r) => (
          <li key={r} className="font-mono text-[11px]">
            {r}
          </li>
        ))}
      </ul>
    </li>
  );
}
