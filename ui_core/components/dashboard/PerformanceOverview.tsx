import { useMemo } from "react";
import { Card } from "@/components/ui/card";
import { PerformanceMetric, InferenceJob } from "@/lib/types";
import { Clock, Gauge, Database, TrendingUp } from "lucide-react";
import { Area, AreaChart, ResponsiveContainer } from "recharts";

interface PerformanceOverviewProps {
  metrics: PerformanceMetric[];
  activeJobs: InferenceJob[];
}

export const PerformanceOverview = ({ metrics, activeJobs }: PerformanceOverviewProps) => {
  const stats = useMemo(() => {
    // Calculate averages from last hour
    const oneHourAgo = Date.now() - 60 * 60 * 1000;
    const recentMetrics = metrics.filter((m) => new Date(m.recorded_at).getTime() > oneHourAgo);

    const latencyMetrics = recentMetrics.filter((m) => m.metric_name === "latency" || m.latency_ms);
    const avgLatency =
      latencyMetrics.length > 0
        ? latencyMetrics.reduce((sum, m) => sum + (m.latency_ms || m.metric_value || 0), 0) /
          latencyMetrics.length
        : 0;

    const throughputMetrics = recentMetrics.filter(
      (m) => m.metric_name === "throughput" || m.throughput_rps,
    );
    const avgThroughput =
      throughputMetrics.length > 0
        ? throughputMetrics.reduce((sum, m) => sum + (m.throughput_rps || m.metric_value || 0), 0) /
          throughputMetrics.length
        : 0;

    const cacheMetrics = recentMetrics.filter(
      (m) => m.metric_name === "cache_hit_ratio" || m.cache_hit_ratio,
    );
    const avgCacheHit =
      cacheMetrics.length > 0
        ? cacheMetrics.reduce((sum, m) => sum + (m.cache_hit_ratio || m.metric_value || 0), 0) /
          cacheMetrics.length
        : 0;

    // Calculate average speedup from jobs
    const jobsWithSpeedup = activeJobs.filter((j) => j.speedup);
    const avgSpeedup =
      jobsWithSpeedup.length > 0
        ? jobsWithSpeedup.reduce((sum, j) => sum + (j.speedup || 0), 0) / jobsWithSpeedup.length
        : 0;

    // Generate sparkline data - HONEST: only use real metrics, no random data
    const generateSparkline = (key: string) => {
      const filtered = recentMetrics
        .filter(
          (m) =>
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
            m.metric_name === key || (m as any)[key],
        )
        .slice(-20);
      return filtered.map((m, i) => ({
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        value: (m as any)[key] || m.metric_value || 0, // Use 0 not random
        index: i,
      }));
    };

    return {
      latency: { value: avgLatency, sparkline: generateSparkline("latency_ms") },
      throughput: { value: avgThroughput, sparkline: generateSparkline("throughput_rps") },
      cacheHit: { value: avgCacheHit * 100, sparkline: generateSparkline("cache_hit_ratio") },
      speedup: { value: avgSpeedup * 100, sparkline: [] },
    };
  }, [metrics, activeJobs]);

  const cards = [
    {
      label: "Avg Latency",
      value: stats.latency.value.toFixed(1),
      unit: "ms",
      icon: Clock,
      sparkline: stats.latency.sparkline,
      color: "hsl(var(--primary))",
    },
    {
      label: "Throughput",
      value: stats.throughput.value.toFixed(1),
      unit: "req/s",
      icon: Gauge,
      sparkline: stats.throughput.sparkline,
      color: "hsl(88, 72%, 60%)",
    },
    {
      label: "Cache Hit",
      value: stats.cacheHit.value.toFixed(1),
      unit: "%",
      icon: Database,
      sparkline: stats.cacheHit.sparkline,
      color: "hsl(200, 72%, 50%)",
    },
    {
      label: "Avg Speedup",
      value: stats.speedup.value.toFixed(1),
      unit: "%",
      icon: TrendingUp,
      sparkline: stats.speedup.sparkline,
      color: "hsl(300, 72%, 50%)",
    },
  ];

  return (
    <Card className="p-6 bg-card border-border">
      <h3 className="text-lg font-semibold mb-6">Performance Overview</h3>

      <div className="grid grid-cols-2 gap-4">
        {cards.map((card) => (
          <div key={card.label} className="p-4 rounded-lg bg-muted/30 border border-border">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2 text-muted-foreground">
                <card.icon className="h-4 w-4" />
                <span className="text-xs">{card.label}</span>
              </div>
            </div>
            <div className="text-2xl font-bold mb-2">
              {card.value}
              <span className="text-sm font-normal text-muted-foreground ml-1">{card.unit}</span>
            </div>
            {card.sparkline.length > 0 && (
              <div className="h-8">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={card.sparkline}>
                    <Area
                      type="monotone"
                      dataKey="value"
                      stroke={card.color}
                      fill={card.color}
                      fillOpacity={0.2}
                      strokeWidth={1.5}
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            )}
          </div>
        ))}
      </div>
    </Card>
  );
};
