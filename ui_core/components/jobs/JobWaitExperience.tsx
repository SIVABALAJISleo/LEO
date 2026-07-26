// JobWaitExperience - Transparent, premium wait experience
// Shows clear status without exposing internal algorithms

import { useState, useEffect } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { Clock, CheckCircle2, Loader2, Bell, Sparkles, Zap } from "lucide-react";
import { cn } from "@/lib/utils";

export type JobWaitStatus = "instant" | "computing" | "queued";

export interface JobWaitProps {
  jobId: string;
  status: JobWaitStatus;
  progress?: number;
  estimatedTimeRange?: { min: string; max: string };
  hasApproximate?: boolean;
  approximateConfidence?: number;
  onAcceptApproximate?: () => void;
  onWaitForExact?: () => void;
  onEnableNotification?: (enabled: boolean) => void;
  className?: string;
}

const STATUS_CONFIG = {
  instant: {
    icon: CheckCircle2,
    label: "Ready",
    description: "Your result is available",
    color: "text-green-500",
    bgColor: "bg-green-500/10 border-green-500/30",
  },
  computing: {
    icon: Loader2,
    label: "Processing",
    description: "Working on your request",
    color: "text-blue-500",
    bgColor: "bg-blue-500/10 border-blue-500/30",
  },
  queued: {
    icon: Clock,
    label: "In Queue",
    description: "Your request is scheduled",
    color: "text-amber-500",
    bgColor: "bg-amber-500/10 border-amber-500/30",
  },
};

// Progress milestones for visual feedback
const MILESTONES = [
  { value: 0, label: "Started" },
  { value: 25, label: "Preparing" },
  { value: 50, label: "Working" },
  { value: 75, label: "Finishing" },
  { value: 100, label: "Complete" },
];

export function JobWaitExperience({
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  jobId,
  status,
  progress = 0,
  estimatedTimeRange,
  hasApproximate,
  approximateConfidence,
  onAcceptApproximate,
  onWaitForExact,
  onEnableNotification,
  className,
}: JobWaitProps) {
  const [notifyWhenReady, setNotifyWhenReady] = useState(false);
  const [animatedProgress, setAnimatedProgress] = useState(0);

  const config = STATUS_CONFIG[status];
  const StatusIcon = config.icon;

  // Smooth progress animation
  useEffect(() => {
    const timer = setTimeout(() => {
      setAnimatedProgress(progress);
    }, 100);
    return () => clearTimeout(timer);
  }, [progress]);

  // Get current milestone
  const currentMilestone = MILESTONES.reduce((prev, curr) =>
    animatedProgress >= curr.value ? curr : prev,
  );

  const handleNotificationToggle = (enabled: boolean) => {
    setNotifyWhenReady(enabled);
    onEnableNotification?.(enabled);
  };

  return (
    <Card className={cn("border", config.bgColor, className)}>
      <CardContent className="pt-6">
        {/* Status Header */}
        <div className="flex items-center gap-3 mb-4">
          <div className={cn("p-2 rounded-full", config.bgColor)}>
            <StatusIcon
              className={cn("h-5 w-5", config.color, status === "computing" && "animate-spin")}
            />
          </div>
          <div className="flex-1">
            <div className="flex items-center gap-2">
              <span className="font-semibold">{config.label}</span>
              <Badge variant="outline" className="text-xs">
                {currentMilestone.label}
              </Badge>
            </div>
            <p className="text-sm text-muted-foreground">{config.description}</p>
          </div>
        </div>

        {/* Progress Bar */}
        {status !== "instant" && (
          <div className="space-y-2 mb-4">
            <Progress value={animatedProgress} className="h-2 transition-all duration-500" />
            <div className="flex justify-between text-xs text-muted-foreground">
              <span>{Math.round(animatedProgress)}%</span>
              {estimatedTimeRange && (
                <span>
                  {estimatedTimeRange.min} – {estimatedTimeRange.max}
                </span>
              )}
            </div>
          </div>
        )}

        {/* Milestones Visual */}
        {status === "computing" && (
          <div className="flex justify-between mb-4">
            {MILESTONES.slice(0, -1).map((milestone) => (
              <div
                key={milestone.value}
                className={cn(
                  "flex flex-col items-center gap-1",
                  animatedProgress >= milestone.value ? "text-primary" : "text-muted-foreground/50",
                )}
              >
                <div
                  className={cn(
                    "w-2 h-2 rounded-full transition-colors",
                    animatedProgress >= milestone.value ? "bg-primary" : "bg-muted-foreground/30",
                  )}
                />
                <span className="text-xs">{milestone.label}</span>
              </div>
            ))}
          </div>
        )}

        {/* Approximate Result Option */}
        {hasApproximate && status !== "instant" && (
          <div className="bg-background/50 rounded-lg p-4 mb-4 border border-border/50">
            <div className="flex items-start gap-3">
              <Sparkles className="h-5 w-5 text-primary mt-0.5" />
              <div className="flex-1">
                <p className="font-medium text-sm">Quick Result Available</p>
                <p className="text-xs text-muted-foreground mb-3">
                  Preview ready now (
                  {approximateConfidence ? `${Math.round(approximateConfidence * 100)}%` : "~70%"}{" "}
                  match)
                </p>
                <div className="flex gap-2">
                  <Button
                    size="sm"
                    variant="default"
                    onClick={onAcceptApproximate}
                    className="gap-1"
                  >
                    <Zap className="h-3 w-3" />
                    Use Quick Result
                  </Button>
                  <Button size="sm" variant="outline" onClick={onWaitForExact}>
                    Wait for Full
                  </Button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Notification Toggle */}
        {status !== "instant" && onEnableNotification && (
          <div className="flex items-center justify-between pt-3 border-t border-border/50">
            <div className="flex items-center gap-2">
              <Bell className="h-4 w-4 text-muted-foreground" />
              <Label htmlFor="notify" className="text-sm cursor-pointer">
                Notify when ready
              </Label>
            </div>
            <Switch
              id="notify"
              checked={notifyWhenReady}
              onCheckedChange={handleNotificationToggle}
            />
          </div>
        )}
      </CardContent>
    </Card>
  );
}
