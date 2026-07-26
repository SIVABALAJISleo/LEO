/**
 * DeviceRegistry - Shows the registered HIPER computational core.
 */

import { useState, useEffect, useCallback } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Server, Laptop, Wifi, RefreshCw, Cpu, ShieldCheck } from "lucide-react";
import { cn } from "@/lib/utils";
import { Skeleton } from "@/components/ui/skeleton";
import { HealthMonitor, SystemHealth } from "@/lib/core/HealthMonitor";

export function DeviceRegistry() {
  const [health, setHealth] = useState<SystemHealth | null>(null);
  const [loading, setLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);

  const fetchEngineStatus = useCallback(async () => {
    try {
      const monitor = HealthMonitor.getInstance();
      const status = await monitor.getSystemHealth();
      setHealth(status);
    } catch (error) {
      console.error("[DeviceRegistry] Failed to fetch engine status:", error);
    } finally {
      setLoading(false);
      setIsRefreshing(false);
    }
  }, []);

  useEffect(() => {
    fetchEngineStatus();
    const interval = setInterval(fetchEngineStatus, 15000);
    return () => clearInterval(interval);
  }, [fetchEngineStatus]);

  const handleRefresh = () => {
    setIsRefreshing(true);
    fetchEngineStatus();
  };

  if (loading) {
    return (
      <Card className="bg-card border-border">
        <CardHeader>
          <Skeleton className="h-6 w-32" />
          <Skeleton className="h-4 w-48" />
        </CardHeader>
        <CardContent className="space-y-3">
          <Skeleton className="h-20 w-full" />
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="bg-card border-border shadow-card overflow-hidden">
      <CardHeader className="border-b border-border/50 bg-muted/30">
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2 text-xl">
              <Server className="h-5 w-5 text-primary" />
              Computational Core
            </CardTitle>
            <CardDescription>Local-first engine registry and capability map</CardDescription>
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={handleRefresh}
            disabled={isRefreshing}
            className="gap-2"
          >
            <RefreshCw className={cn("h-4 w-4", isRefreshing && "animate-spin")} />
            Sync Status
          </Button>
        </div>
      </CardHeader>
      <CardContent className="pt-6">
        <div className="space-y-4">
          {/* Main Local Engine */}
          <div
            className={cn(
              "p-5 rounded-xl border transition-all duration-300",
              health?.status === "healthy"
                ? "border-primary/20 bg-primary/5 shadow-[0_0_15px_-5px_hsl(var(--primary)/0.2)]"
                : "border-muted bg-muted/5",
            )}
          >
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
              <div className="flex items-start gap-4">
                <div
                  className={cn(
                    "p-3 rounded-xl",
                    health?.status === "healthy"
                      ? "bg-primary/10 text-primary"
                      : "bg-muted text-muted-foreground",
                  )}
                >
                  <Laptop className="h-6 w-6" />
                </div>

                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-lg">Local SaaS Core</span>
                    <Badge
                      variant="default"
                      className="bg-primary/20 text-primary hover:bg-primary/20 border-primary/20"
                    >
                      Primary
                    </Badge>
                  </div>

                  <div className="flex flex-wrap items-center gap-4 mt-2">
                    <span className="flex items-center gap-1.5 text-xs font-medium text-green-500">
                      <Wifi className="h-3.5 w-3.5" />
                      Connected
                    </span>

                    <span className="flex items-center gap-1.5 text-xs text-muted-foreground">
                      <Cpu className="h-3.5 w-3.5" />
                      {Math.round((health?.memory.used || 0) / (1024 * 1024))} MB used
                    </span>

                    <span className="flex items-center gap-1.5 text-xs text-muted-foreground">
                      <ShieldCheck className="h-3.5 w-3.5" />
                      Safe Compute V3
                    </span>
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-3">
                <div className="text-right hidden sm:block">
                  <p className="text-[10px] uppercase tracking-wider text-muted-foreground font-semibold">
                    Uptime
                  </p>
                  <p className="text-sm font-mono font-bold text-primary">{health?.uptime}s</p>
                </div>
                <div className="h-10 w-[1px] bg-border/50 mx-2 hidden sm:block" />
                <Badge
                  variant="outline"
                  className="h-7 px-3 border-primary/30 text-primary bg-primary/5 hidden md:flex"
                >
                  CPU-Optimized
                </Badge>
              </div>
            </div>

            {/* Capability Bar */}
            <div className="mt-6 pt-5 border-t border-border/50">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {[
                  { label: "Intelligence", status: "Active" },
                  { label: "Orchestration", status: "Active" },
                  { label: "Safe Execution", status: "Enforced" },
                  { label: "Resource Mgmt", status: "Optimal" },
                ].map((cap, i) => (
                  <div key={i} className="space-y-1">
                    <p className="text-[10px] uppercase text-muted-foreground font-bold">
                      {cap.label}
                    </p>
                    <p className="text-xs font-medium text-foreground">{cap.status}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Cloud Info */}
          <div className="p-4 rounded-lg bg-muted/20 border border-dashed border-border/50 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded bg-muted">
                <Server className="h-4 w-4 text-muted-foreground" />
              </div>
              <div className="text-sm">
                <p className="font-medium text-muted-foreground">Cloud Uplink Not Required</p>
                <p className="text-xs text-muted-foreground/60">
                  System is currently operating in total-isolation mode.
                </p>
              </div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

export default DeviceRegistry;
