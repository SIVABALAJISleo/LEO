/**
 * DataSourceIndicator - Shows where data comes from
 *
 * PRODUCTION HONESTY:
 * - Clearly marks data as REAL (from agent), DELEGATED (cloud), or DEMO
 * - Never misleads users about data origin
 */

import { Badge } from "@/components/ui/badge";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { Server, Cloud, FlaskConical, AlertCircle } from "lucide-react";
import { cn } from "@/lib/utils";

export type DataSource = "agent" | "cloud" | "demo" | "unavailable";

interface DataSourceIndicatorProps {
  source: DataSource;
  lastUpdated?: Date;
  className?: string;
  showLabel?: boolean;
}

const sourceConfig: Record<
  DataSource,
  {
    icon: typeof Server;
    label: string;
    description: string;
    badgeVariant: "default" | "secondary" | "destructive" | "outline";
    color: string;
  }
> = {
  agent: {
    icon: Server,
    label: "Local Agent",
    description: "Real metrics from your local machine via installed agent",
    badgeVariant: "default",
    color: "text-primary",
  },
  cloud: {
    icon: Cloud,
    label: "Cloud",
    description: "Metrics from cloud infrastructure (delegated workloads)",
    badgeVariant: "secondary",
    color: "text-blue-500",
  },
  demo: {
    icon: FlaskConical,
    label: "Demo",
    description: "Sample data for demonstration purposes only",
    badgeVariant: "outline",
    color: "text-yellow-500",
  },
  unavailable: {
    icon: AlertCircle,
    label: "Unavailable",
    description: "No data source connected",
    badgeVariant: "destructive",
    color: "text-destructive",
  },
};

export const DataSourceIndicator = ({
  source,
  lastUpdated,
  className,
  showLabel = true,
}: DataSourceIndicatorProps) => {
  const config = sourceConfig[source];
  const Icon = config.icon;

  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger asChild>
          <Badge variant={config.badgeVariant} className={cn("gap-1.5 cursor-help", className)}>
            <Icon className={cn("h-3 w-3", config.color)} />
            {showLabel && <span>{config.label}</span>}
          </Badge>
        </TooltipTrigger>
        <TooltipContent side="bottom" className="max-w-xs">
          <p className="font-medium">{config.label}</p>
          <p className="text-xs text-muted-foreground mt-1">{config.description}</p>
          {lastUpdated && (
            <p className="text-xs text-muted-foreground mt-1">
              Last updated: {lastUpdated.toLocaleTimeString()}
            </p>
          )}
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
};

export default DataSourceIndicator;
