import { useState, useEffect } from "react";
// eslint-disable-next-line @typescript-eslint/no-unused-vars
import { X, TrendingUp, AlertTriangle, Clock, CheckCircle, XCircle } from "lucide-react";
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";
import { Badge } from "@/components/ui/badge";
// eslint-disable-next-line @typescript-eslint/no-unused-vars
import { Progress } from "@/components/ui/progress";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { ModuleData, ModuleStats, useModulesData } from "@/hooks/useModulesData";
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart";
import { LineChart, Line, XAxis, YAxis, ResponsiveContainer, Legend } from "recharts";
import { cn } from "@/lib/utils";

interface StatsDrawerProps {
  module: ModuleData | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function StatsDrawer({ module, open, onOpenChange }: StatsDrawerProps) {
  const { fetchModuleStats } = useModulesData();
  const [stats, setStats] = useState<ModuleStats | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (module && open) {
      setLoading(true);
      fetchModuleStats(module.name).then((data) => {
        setStats(data);
        setLoading(false);
      });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [module, open]);

  if (!module) return null;

  const chartData =
    stats?.performanceHistory
      .slice(0, 30)
      .reverse()
      .map((item, idx) => ({
        index: idx,
        speedup: item.speedup,
        compression: item.compression,
        date: new Date(item.recorded_at).toLocaleDateString(),
      })) || [];

  const getSeverityColor = (severity: string) => {
    switch (severity.toLowerCase()) {
      case "critical":
      case "error":
        return "bg-red-500/20 text-red-400 border-red-500/30";
      case "warning":
        return "bg-yellow-500/20 text-yellow-400 border-yellow-500/30";
      default:
        return "bg-blue-500/20 text-blue-400 border-blue-500/30";
    }
  };

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent className="w-full sm:max-w-lg overflow-hidden">
        <SheetHeader>
          <SheetTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5" />
            {module.name} Statistics
          </SheetTitle>
          <SheetDescription>Detailed performance metrics and history</SheetDescription>
        </SheetHeader>

        <ScrollArea className="h-[calc(100vh-120px)] mt-6 pr-4">
          {loading ? (
            <div className="flex items-center justify-center h-64 text-muted-foreground">
              Loading statistics...
            </div>
          ) : (
            <div className="space-y-6">
              {/* Summary Stats */}
              <div className="grid grid-cols-2 gap-4">
                <div className="p-4 bg-card rounded-lg border border-border">
                  <p className="text-xs text-muted-foreground uppercase tracking-wide">
                    Total Runs
                  </p>
                  <p className="text-2xl font-bold text-foreground">{stats?.totalRuns || 0}</p>
                </div>
                <div className="p-4 bg-card rounded-lg border border-border">
                  <p className="text-xs text-muted-foreground uppercase tracking-wide">
                    Success Rate
                  </p>
                  <div className="flex items-center gap-2">
                    <p className="text-2xl font-bold text-foreground">
                      {(stats?.successRate || 0).toFixed(1)}%
                    </p>
                    {(stats?.successRate || 0) >= 90 ? (
                      <CheckCircle className="h-5 w-5 text-green-500" />
                    ) : (stats?.successRate || 0) >= 70 ? (
                      <AlertTriangle className="h-5 w-5 text-yellow-500" />
                    ) : (
                      <XCircle className="h-5 w-5 text-red-500" />
                    )}
                  </div>
                </div>
                <div className="p-4 bg-card rounded-lg border border-border col-span-2">
                  <p className="text-xs text-muted-foreground uppercase tracking-wide">
                    Avg Latency Impact
                  </p>
                  <div className="flex items-center gap-2">
                    <Clock className="h-4 w-4 text-muted-foreground" />
                    <p className="text-2xl font-bold text-foreground">
                      {(stats?.avgLatencyImpact || 0).toFixed(1)} ms
                    </p>
                  </div>
                </div>
              </div>

              <Separator />

              {/* Performance Chart */}
              <div className="space-y-4">
                <h4 className="text-sm font-semibold text-foreground">Performance Timeline</h4>
                {chartData.length > 0 ? (
                  <ChartContainer
                    config={{
                      speedup: {
                        label: "Speedup",
                        color: "hsl(var(--primary))",
                      },
                      compression: {
                        label: "Compression",
                        color: "hsl(var(--chart-2))",
                      },
                    }}
                    className="h-48"
                  >
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={chartData}>
                        <XAxis dataKey="date" tick={{ fontSize: 10 }} />
                        <YAxis tick={{ fontSize: 10 }} />
                        <ChartTooltip content={<ChartTooltipContent />} />
                        <Legend />
                        <Line
                          type="monotone"
                          dataKey="speedup"
                          stroke="hsl(var(--primary))"
                          strokeWidth={2}
                          dot={false}
                          name="Speedup"
                        />
                        <Line
                          type="monotone"
                          dataKey="compression"
                          stroke="hsl(var(--chart-2))"
                          strokeWidth={2}
                          dot={false}
                          name="Compression"
                        />
                      </LineChart>
                    </ResponsiveContainer>
                  </ChartContainer>
                ) : (
                  <div className="h-48 flex items-center justify-center text-muted-foreground bg-muted/50 rounded-lg">
                    No performance data available
                  </div>
                )}
              </div>

              <Separator />

              {/* Error History */}
              <div className="space-y-4">
                <h4 className="text-sm font-semibold text-foreground flex items-center gap-2">
                  <AlertTriangle className="h-4 w-4" />
                  Error History
                </h4>
                {stats?.errorHistory && stats.errorHistory.length > 0 ? (
                  <div className="space-y-3">
                    {stats.errorHistory.map((error) => (
                      <div
                        key={error.id}
                        className={cn(
                          "p-3 rounded-lg border",
                          error.resolved ? "bg-muted/30 border-border" : "bg-card border-border",
                        )}
                      >
                        <div className="flex items-start justify-between gap-2">
                          <div className="space-y-1 flex-1 min-w-0">
                            <div className="flex items-center gap-2">
                              <Badge
                                variant="outline"
                                className={cn("text-xs", getSeverityColor(error.severity))}
                              >
                                {error.severity}
                              </Badge>
                              {error.resolved && (
                                <Badge
                                  variant="outline"
                                  className="text-xs bg-green-500/20 text-green-400 border-green-500/30"
                                >
                                  Resolved
                                </Badge>
                              )}
                            </div>
                            <p className="text-sm font-medium text-foreground truncate">
                              {error.title}
                            </p>
                            <p className="text-xs text-muted-foreground line-clamp-2">
                              {error.message}
                            </p>
                          </div>
                          <span className="text-xs text-muted-foreground whitespace-nowrap">
                            {new Date(error.created_at).toLocaleDateString()}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="p-8 text-center text-muted-foreground bg-muted/50 rounded-lg">
                    <CheckCircle className="h-8 w-8 mx-auto mb-2 text-green-500" />
                    <p className="text-sm">No errors recorded</p>
                  </div>
                )}
              </div>
            </div>
          )}
        </ScrollArea>
      </SheetContent>
    </Sheet>
  );
}
