// eslint-disable-next-line @typescript-eslint/no-unused-vars
import { Zap, Settings, BarChart3, Check } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import { Progress } from "@/components/ui/progress";
import { Checkbox } from "@/components/ui/checkbox";
import { ModuleData } from "@/hooks/useModulesData";
import { cn } from "@/lib/utils";

interface ModuleCardProps {
  module: ModuleData;
  isSelected: boolean;
  onSelect: (selected: boolean) => void;
  onToggleEnabled: (enabled: boolean) => void;
  onConfigure: () => void;
  onViewStats: () => void;
}

export function ModuleCard({
  module,
  isSelected,
  onSelect,
  onToggleEnabled,
  onConfigure,
  onViewStats,
}: ModuleCardProps) {
  const enabled = module.config?.enabled ?? false;
  // If enabled, force status to active/operational to reflect real-time engine state
  const status = enabled ? "Operational" : module.status?.status || "idle";
  const healthScore = module.status?.health_score ?? 100;
  const speedup = module.config?.speedup_achieved;
  const compression = module.config?.compression_ratio_achieved;

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case "operational":
      case "active":
        return "bg-green-500/20 text-green-400 border-green-500/30";
      case "degraded":
      case "warning":
        return "bg-yellow-500/20 text-yellow-400 border-yellow-500/30";
      case "offline":
      case "error":
        return "bg-red-500/20 text-red-400 border-red-500/30";
      default:
        return "bg-muted text-muted-foreground border-border";
    }
  };

  const getHealthColor = (score: number) => {
    if (score >= 80) return "bg-green-500";
    if (score >= 50) return "bg-yellow-500";
    return "bg-red-500";
  };

  return (
    <Card
      className={cn(
        "relative transition-all duration-200 hover:shadow-lg hover:border-primary/50",
        isSelected && "ring-2 ring-primary border-primary",
      )}
    >
      {/* Selection Checkbox */}
      <div className="absolute top-3 right-3 z-10">
        <Checkbox
          checked={isSelected}
          onCheckedChange={onSelect}
          className="data-[state=checked]:bg-primary"
        />
      </div>

      <CardHeader className="pb-2">
        <div className="flex items-start justify-between pr-8">
          <div className="space-y-1">
            <CardTitle className="text-base font-semibold">{module.name}</CardTitle>
            <Badge variant="outline" className={cn("text-xs", getStatusColor(status))}>
              {status}
            </Badge>
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* Description */}
        <p className="text-sm text-muted-foreground line-clamp-2">{module.description}</p>

        {/* Health Score */}
        <div className="space-y-1.5">
          <div className="flex justify-between text-xs">
            <span className="text-muted-foreground">Health Score</span>
            <span className="font-medium">{healthScore.toFixed(0)}%</span>
          </div>
          <Progress
            value={healthScore}
            className="h-1.5"
            indicatorClassName={getHealthColor(healthScore)}
          />
        </div>

        {/* Metrics */}
        <div className="grid grid-cols-2 gap-2">
          <div className="flex items-center gap-2 p-2 bg-muted/50 rounded-md">
            <Zap className="h-3.5 w-3.5 text-primary" />
            <div className="min-w-0">
              <p className="text-[10px] text-muted-foreground uppercase tracking-wide">Speedup</p>
              <p className="text-sm font-semibold truncate">
                {speedup ? `${speedup.toFixed(2)}x` : "—"}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2 p-2 bg-muted/50 rounded-md">
            <BarChart3 className="h-3.5 w-3.5 text-primary" />
            <div className="min-w-0">
              <p className="text-[10px] text-muted-foreground uppercase tracking-wide">
                Compression
              </p>
              <p className="text-sm font-semibold truncate">
                {compression ? `${compression.toFixed(2)}x` : "—"}
              </p>
            </div>
          </div>
        </div>

        {/* Enable Toggle */}
        <div className="flex items-center justify-between py-2 border-t border-border">
          <span className="text-sm font-medium">Enabled</span>
          <Switch checked={enabled} onCheckedChange={onToggleEnabled} />
        </div>

        {/* Actions */}
        <div className="flex gap-2">
          <Button variant="outline" size="sm" className="flex-1" onClick={onConfigure}>
            <Settings className="h-3.5 w-3.5 mr-1.5" />
            Configure
          </Button>
          <Button variant="ghost" size="sm" className="flex-1" onClick={onViewStats}>
            <BarChart3 className="h-3.5 w-3.5 mr-1.5" />
            Stats
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
