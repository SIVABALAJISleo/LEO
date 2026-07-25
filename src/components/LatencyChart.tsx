import { useHealthHistory } from "@/lib/health-history";

// Small inline SVG sparkline of the last 60 /health latencies.
export function LatencyChart({ width = 560, height = 120 }: { width?: number; height?: number }) {
  const history = useHealthHistory();
  const points = history.filter((h) => typeof h.latencyMs === "number");

  const pad = 8;
  const w = width;
  const h = height;
  const max = Math.max(50, ...points.map((p) => p.latencyMs ?? 0));
  const min = 0;
  const stepX = points.length > 1 ? (w - pad * 2) / (points.length - 1) : 0;
  const y = (v: number) => h - pad - ((v - min) / Math.max(1, max - min)) * (h - pad * 2);

  const path = points
    .map((p, i) => `${i === 0 ? "M" : "L"} ${pad + i * stepX} ${y(p.latencyMs ?? 0)}`)
    .join(" ");

  const last = points[points.length - 1];

  return (
    <div
      className="border border-border bg-background/60 p-4"
      role="img"
      aria-label={`Backend latency over last ${points.length} health checks`}
    >
      <div className="mb-2 flex items-baseline justify-between">
        <div className="eyebrow">Live /health latency</div>
        <div className="font-mono text-xs text-muted-foreground">
          {points.length}/60 samples · max {max}ms
          {last?.latencyMs != null ? ` · last ${last.latencyMs}ms` : ""}
        </div>
      </div>
      <svg
        viewBox={`0 0 ${w} ${h}`}
        width="100%"
        height={h}
        preserveAspectRatio="none"
        className="block"
      >
        <line
          x1={pad}
          x2={w - pad}
          y1={h - pad}
          y2={h - pad}
          stroke="currentColor"
          strokeOpacity={0.15}
        />
        {points.length > 0 && (
          <>
            <path d={path} fill="none" stroke="#76B900" strokeWidth={1.5} />
            {points.map((p, i) => (
              <circle
                key={p.id}
                cx={pad + i * stepX}
                cy={y(p.latencyMs ?? 0)}
                r={2}
                fill={
                  p.status === "online" ? "#76B900" : p.status === "error" ? "#fb923c" : "#ef4444"
                }
              >
                <title>{`${p.latencyMs}ms · ${p.status}${p.httpStatus ? ` · ${p.httpStatus}` : ""}`}</title>
              </circle>
            ))}
          </>
        )}
        {points.length === 0 && (
          <text
            x={w / 2}
            y={h / 2}
            textAnchor="middle"
            className="fill-muted-foreground"
            fontSize="12"
          >
            Waiting for first /health sample…
          </text>
        )}
      </svg>
    </div>
  );
}
