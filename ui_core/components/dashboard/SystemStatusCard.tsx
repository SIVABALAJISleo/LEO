import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { SystemMetrics } from "@/lib/types";
import {
  Cpu,
  HardDrive,
  Thermometer,
  Zap,
  RefreshCw,
  Activity,
  WifiOff,
  Server,
} from "lucide-react";
import { format, formatDistanceToNow } from "date-fns";
import { cn } from "@/lib/utils";
import { DataSourceIndicator, DataSource } from "./DataSourceIndicator";

interface SystemStatusCardProps {
  metrics: SystemMetrics | null;
  onRefresh: () => void;
}

/**
 * SystemStatusCard - Displays system metrics with honest data source indication
 *
 * PRODUCTION HONESTY:
 * - Shows "Awaiting Agent" when no metrics available
 * - Clearly indicates data source (agent vs demo)
 * - Shows stale data warning when metrics are old
 */
export const SystemStatusCard = ({ metrics, onRefresh }: SystemStatusCardProps) => {
  // Determine data freshness and source
  const getDataSource = (): DataSource => {
    if (!metrics) return "unavailable";

    const recordedAt = new Date(metrics.recorded_at);
    const minutesOld = (Date.now() - recordedAt.getTime()) / 1000 / 60;

    // Real agent data should be < 5 minutes old
    if (minutesOld < 5) return "agent";
    // Stale data or demo data
    if (minutesOld < 60) return "cloud";
    return "demo";
  };

  const dataSource = getDataSource();
  const isStale = metrics && Date.now() - new Date(metrics.recorded_at).getTime() > 5 * 60 * 1000;

  const getProgressColor = (value: number, thresholds = { warning: 70, critical: 90 }) => {
    if (value >= thresholds.critical) return "bg-destructive";
    if (value >= thresholds.warning) return "bg-yellow-500";
    return "bg-primary";
  };

  const stats = [
    {
      label: "CPU",
      value: metrics?.cpu_percent ?? metrics?.gpu_utilization ?? 0,
      unit: "%",
      icon: Cpu,
      max: 100,
    },
    {
      label: "Memory",
      value: metrics?.memory_usage ?? 0,
      unit: "MB",
      icon: Activity,
      max: 32000,
    },
    {
      label: "Disk",
      value: metrics?.disk_gb ?? 0,
      unit: "GB",
      icon: HardDrive,
      max: 1000,
    },
    {
      label: "Temperature",
      value: metrics?.temperature ?? 0,
      unit: "°C",
      icon: Thermometer,
      max: 100,
      thresholds: { warning: 70, critical: 85 },
    },
    {
      label: "Active Jobs",
      value: metrics?.active_jobs ?? 0,
      unit: "",
      icon: Zap,
      max: 10,
    },
  ];

  return (
    <Card className="p-6 bg-card border-border">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <h3 className="text-lg font-semibold">System Status</h3>
          <DataSourceIndicator source={dataSource} />
        </div>
        <div className="flex items-center gap-2">
          {metrics?.recorded_at && (
            <span className={cn("text-xs", isStale ? "text-yellow-500" : "text-muted-foreground")}>
              {isStale ? "Stale: " : "Updated "}
              {format(new Date(metrics.recorded_at), "HH:mm:ss")}
            </span>
          )}
          <Button variant="ghost" size="icon" onClick={onRefresh}>
            <RefreshCw className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {!metrics ? (
        // No metrics - show honest "awaiting agent" state
        <div className="text-center py-8 border rounded-lg border-dashed border-muted">
          <WifiOff className="h-12 w-12 mx-auto mb-3 text-muted-foreground/50" />
          <h4 className="font-medium text-foreground mb-2">Awaiting Agent Connection</h4>
          <p className="text-sm text-muted-foreground mb-4 max-w-md mx-auto">
            Hardware metrics (CPU, GPU, RAM, temperature) require a local agent running on your
            machine. Browsers cannot access this data directly.
          </p>
          <div className="flex items-center justify-center gap-4 text-xs text-muted-foreground">
            <div className="flex items-center gap-1.5">
              <Server className="h-3.5 w-3.5" />
              <span>Install agent to see real metrics</span>
            </div>
          </div>
        </div>
      ) : (
        // Has metrics - show them with source indicator
        <>
          {isStale && (
            <div className="mb-4 px-3 py-2 rounded-md bg-yellow-500/10 border border-yellow-500/20 text-sm text-yellow-600 dark:text-yellow-400">
              ⚠️ Metrics are{" "}
              {formatDistanceToNow(new Date(metrics.recorded_at), { addSuffix: false })} old. Agent
              may be disconnected.
            </div>
          )}

          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
            {stats.map((stat) => {
              const percentage = (stat.value / stat.max) * 100;
              const thresholds = stat.thresholds || { warning: 70, critical: 90 };

              return (
                <div key={stat.label} className="space-y-2">
                  <div className="flex items-center gap-2 text-muted-foreground">
                    <stat.icon className="h-4 w-4" />
                    <span className="text-xs">{stat.label}</span>
                  </div>
                  <div className="text-2xl font-bold">
                    {stat.value.toFixed(stat.unit === "%" ? 1 : 0)}
                    <span className="text-sm font-normal text-muted-foreground ml-1">
                      {stat.unit}
                    </span>
                  </div>
                  <div className="h-1.5 bg-muted rounded-full overflow-hidden">
                    <div
                      className={cn(
                        "h-full transition-all duration-500",
                        getProgressColor(percentage, thresholds),
                      )}
                      style={{ width: `${Math.min(percentage, 100)}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </>
      )}
    </Card>
  );
};
