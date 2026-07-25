// Compact bar chart of the last 30 health checks. Green = online, red =
// failure; bar height encodes latency. Overlays alert-timeline episodes as
// shaded regions with start/end markers so latency spikes correlate to
// warn/critical alert episodes.
import { useMemo } from "react";
import { useHealthHistory } from "@/lib/health-history";
import { useAlertTimeline, type AlertEvent } from "@/lib/health-alert-timeline";

const N = 30;

export function HealthHistoryChart() {
  const history = useHealthHistory();
  const timeline = useAlertTimeline();
  const slice = useMemo(() => history.slice(-N), [history]);

  const maxLatency = useMemo(() => Math.max(100, ...slice.map((e) => e.latencyMs ?? 0)), [slice]);

  const okCount = slice.filter((e) => e.status === "online").length;
  const failCount = slice.filter((e) => e.status !== "online" && e.status !== "checking").length;
  const avgLatency = (() => {
    const oks = slice.filter((e) => e.status === "online" && typeof e.latencyMs === "number");
    if (!oks.length) return null;
    return Math.round(oks.reduce((s, e) => s + (e.latencyMs ?? 0), 0) / oks.length);
  })();

  // Time-window of the visible slice, used to project alert episodes onto
  // the bar strip as shaded regions. If no bar has a timestamp, we skip.
  const timeExtent = useMemo(() => {
    const times = slice.map((e) => e.checkedAt ?? 0).filter((t) => t > 0);
    if (times.length < 2) return null;
    return { start: times[0], end: times[times.length - 1] };
  }, [slice]);

  // Episodes overlapping the visible window (open episodes count as "now").
  const overlapping = useMemo<AlertEvent[]>(() => {
    if (!timeExtent) return [];
    const now = Date.now();
    return timeline.filter((ep) => {
      const s = ep.startedAt;
      const e = ep.endedAt ?? now;
      return e >= timeExtent.start && s <= timeExtent.end;
    });
  }, [timeline, timeExtent]);

  function pctFor(ts: number): number {
    if (!timeExtent) return 0;
    const span = Math.max(1, timeExtent.end - timeExtent.start);
    return Math.max(0, Math.min(100, ((ts - timeExtent.start) / span) * 100));
  }

  return (
    <div id="health-history-chart" className="border border-border p-4">
      <div className="flex flex-wrap items-baseline justify-between gap-2">
        <div>
          <p className="eyebrow">Last {N} health checks</p>
          <p className="mt-1 text-xs text-muted-foreground">
            Bar height = latency · color = status · shaded band = alert episode
          </p>
        </div>
        <div className="flex gap-4 text-xs">
          <Stat label="OK" value={okCount} tone="ok" />
          <Stat label="Fail" value={failCount} tone="fail" />
          <Stat label="Avg" value={avgLatency != null ? `${avgLatency}ms` : "—"} />
          <Stat
            label="Alerts"
            value={overlapping.length}
            tone={overlapping.length ? "fail" : undefined}
          />
        </div>
      </div>

      <div
        className="relative mt-4 h-24"
        role="img"
        aria-label={`Latency history for last ${slice.length} checks with ${overlapping.length} alert episodes overlaid`}
      >
        {/* Alert-episode overlays: shaded rectangles + start/end markers.
            Render behind the bars so latency stays legible. */}
        {timeExtent && overlapping.length > 0 && (
          <div className="pointer-events-none absolute inset-0 z-0">
            {overlapping.map((ep) => {
              const startPct = pctFor(ep.startedAt);
              const endPct = pctFor(ep.endedAt ?? Date.now());
              const widthPct = Math.max(0.5, endPct - startPct);
              const isCritical = ep.peakLevel === "critical";
              const bg = isCritical ? "bg-red-500/15" : "bg-yellow-400/15";
              const border = isCritical ? "border-red-500/60" : "border-yellow-400/60";
              const title = `${isCritical ? "Critical" : "Warn"} · ${new Date(ep.startedAt).toLocaleTimeString()}${
                ep.endedAt ? ` → ${new Date(ep.endedAt).toLocaleTimeString()}` : " (ongoing)"
              }${ep.lastReasons.length ? "\n" + ep.lastReasons.join("\n") : ""}`;
              return (
                <div
                  key={ep.id}
                  className={`absolute top-0 bottom-0 border-x ${bg} ${border}`}
                  style={{ left: `${startPct}%`, width: `${widthPct}%` }}
                  title={title}
                />
              );
            })}
          </div>
        )}

        <div className="relative z-10 flex h-full items-end gap-1">
          {slice.length === 0 && (
            <p className="w-full text-center text-xs text-muted-foreground">
              No checks yet — waiting for first poll.
            </p>
          )}
          {slice.map((e) => {
            const ok = e.status === "online";
            const height =
              e.latencyMs != null ? Math.max(4, Math.round((e.latencyMs / maxLatency) * 96)) : 96;
            const color = ok ? "bg-leo" : e.status === "checking" ? "bg-yellow-400" : "bg-red-500";
            const title = [
              e.checkedAt ? new Date(e.checkedAt).toLocaleTimeString() : "",
              e.status,
              e.latencyMs != null ? `${e.latencyMs}ms` : "",
              e.httpStatus ? `HTTP ${e.httpStatus}` : "",
              e.message ?? "",
            ]
              .filter(Boolean)
              .join(" · ");
            return (
              <div
                key={e.id}
                className={`flex-1 ${color} transition-all hover:opacity-80`}
                style={{ height: `${height}%`, minWidth: 4 }}
                title={title}
              />
            );
          })}
          {slice.length > 0 &&
            Array.from({ length: N - slice.length }).map((_, i) => (
              <div key={`pad-${i}`} className="h-1 flex-1 bg-border/40" style={{ minWidth: 4 }} />
            ))}
        </div>
      </div>

      <div className="mt-2 flex justify-between text-[10px] text-muted-foreground">
        <span>older</span>
        <span>0–{maxLatency}ms range</span>
        <span>newest</span>
      </div>

      {overlapping.length > 0 && (
        <ul className="mt-3 space-y-1 border-t border-border pt-2 text-[11px]">
          {overlapping.map((ep) => {
            const isCritical = ep.peakLevel === "critical";
            const dot = isCritical ? "bg-red-500" : "bg-yellow-400";
            const duration = Math.round(((ep.endedAt ?? Date.now()) - ep.startedAt) / 1000);
            return (
              <li key={ep.id} className="flex items-start gap-2">
                <span className={`mt-1 inline-block h-2 w-2 shrink-0 ${dot}`} />
                <span className="flex-1">
                  <span className="font-semibold uppercase tracking-wide">{ep.peakLevel}</span>{" "}
                  <span className="text-muted-foreground">
                    {new Date(ep.startedAt).toLocaleTimeString()}
                    {ep.endedAt
                      ? ` → ${new Date(ep.endedAt).toLocaleTimeString()} (${duration}s)`
                      : " · ongoing"}
                  </span>
                  {ep.lastReasons.length > 0 && (
                    <span className="ml-1 text-muted-foreground">
                      — {ep.lastReasons.join("; ")}
                    </span>
                  )}
                </span>
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}

function Stat({
  label,
  value,
  tone,
}: {
  label: string;
  value: number | string;
  tone?: "ok" | "fail";
}) {
  const color = tone === "ok" ? "text-leo" : tone === "fail" ? "text-red-400" : "text-foreground";
  return (
    <div className="text-right">
      <div className="text-[10px] uppercase tracking-wide text-muted-foreground">{label}</div>
      <div className={`font-mono text-sm font-semibold ${color}`}>{value}</div>
    </div>
  );
}
