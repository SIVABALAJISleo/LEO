/**
 * AgentStatusBanner - Shows the connection status of the local HYPER engine
 */

import { useState, useEffect, useCallback } from "react";
// eslint-disable-next-line @typescript-eslint/no-unused-vars
import { useAuth } from "@/contexts/AuthContext";
// eslint-disable-next-line @typescript-eslint/no-unused-vars
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Wifi, WifiOff, Clock, RefreshCw, Cpu, Activity } from "lucide-react";
import { cn } from "@/lib/utils";
import { HealthMonitor, SystemHealth } from "@/lib/core/HealthMonitor";

interface AgentStatusBannerProps {
  className?: string;
  compact?: boolean;
}

export const AgentStatusBanner = ({ className, compact = false }: AgentStatusBannerProps) => {
  const [health, setHealth] = useState<SystemHealth | null>(null);
  const [isChecking, setIsChecking] = useState(false);

  const checkEngineStatus = useCallback(async () => {
    setIsChecking(true);
    try {
      const monitor = HealthMonitor.getInstance();
      const status = await monitor.getSystemHealth();
      setHealth(status);
    } catch (error) {
      console.error("[EngineStatus] Check failed:", error);
    } finally {
      setIsChecking(false);
    }
  }, []);

  useEffect(() => {
    checkEngineStatus();
    const interval = setInterval(checkEngineStatus, 15000);
    return () => clearInterval(interval);
  }, [checkEngineStatus]);

  const getStatusConfig = () => {
    if (!health) {
      return {
        icon: RefreshCw,
        label: "Initializing...",
        description: "Warming up HYPER intelligence layers",
        variant: "default" as const,
        badgeVariant: "outline" as const,
        className: "border-muted",
      };
    }

    switch (health.status) {
      case "healthy":
        return {
          icon: Wifi,
          label: "HYPER Engine Online",
          description: `Localized SaaS Core active. Uptime: ${health.uptime}s`,
          variant: "default" as const,
          badgeVariant: "default" as const,
          className: "border-primary/30 bg-primary/5",
        };
      case "degraded":
        return {
          icon: Clock,
          label: "Engine Degraded",
          description: "Running in performance-safe mode.",
          variant: "default" as const,
          badgeVariant: "secondary" as const,
          className: "border-yellow-500/30 bg-yellow-500/5",
        };
      case "unhealthy":
      default:
        return {
          icon: WifiOff,
          label: "Engine Offline",
          description: "Internal engine has stalled. Refresh required.",
          variant: "destructive" as const,
          badgeVariant: "destructive" as const,
          className: "border-destructive/30 bg-destructive/5",
        };
    }
  };

  const config = getStatusConfig();
  const StatusIcon = config.icon;

  if (compact) {
    return (
      <Badge variant={config.badgeVariant} className={cn("gap-1.5", className)}>
        <StatusIcon className={cn("h-3 w-3", !health && "animate-spin")} />
        {config.label}
      </Badge>
    );
  }

  return (
    <div
      className={cn(
        "flex items-center gap-3 px-4 py-2 rounded-lg border",
        config.className,
        className,
      )}
    >
      <StatusIcon
        className={cn(
          "h-4 w-4",
          !health && "animate-spin",
          health?.status === "healthy" ? "text-primary" : "",
        )}
      />
      <div className="flex-1 text-sm">
        <span className="font-medium text-primary">{config.label}</span>
        <span className="text-muted-foreground ml-3 hidden sm:inline border-l border-border pl-3">
          {config.description}
        </span>
      </div>
      <div className="flex items-center gap-2">
        {health && (
          <div className="flex items-center gap-3 mr-4 text-xs font-mono text-muted-foreground hidden md:flex">
            <div className="flex items-center gap-1">
              <Cpu className="h-3 w-3" />
              {Math.round((health.memory.used / health.memory.total) * 100)}%
            </div>
            <div className="flex items-center gap-1">
              <Activity className="h-3 w-3" />
              {health.uptime}s
            </div>
          </div>
        )}
        <Button
          variant="ghost"
          size="sm"
          className="h-8 w-8 p-0"
          onClick={checkEngineStatus}
          disabled={isChecking}
        >
          <RefreshCw className={cn("h-4 w-4", isChecking && "animate-spin")} />
        </Button>
      </div>
    </div>
  );
};

export default AgentStatusBanner;
