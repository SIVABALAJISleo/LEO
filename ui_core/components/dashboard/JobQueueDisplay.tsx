import { Clock, Loader2, CheckCircle, XCircle, Pause } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { useSafeCompute } from "@/hooks/useSafeCompute";
import { cn } from "@/lib/utils";

export const JobQueueDisplay = () => {
  const { queueStats, jobs } = useSafeCompute();

  const formatTime = (seconds: number): string => {
    if (seconds < 60) return `${Math.round(seconds)}s`;
    if (seconds < 3600) return `${Math.round(seconds / 60)}m`;
    return `${Math.round(seconds / 3600)}h`;
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "processing":
        return <Loader2 className="h-4 w-4 animate-spin text-primary" />;
      case "completed":
        return <CheckCircle className="h-4 w-4 text-primary" />;
      case "failed":
        return <XCircle className="h-4 w-4 text-destructive" />;
      case "paused":
        return <Pause className="h-4 w-4 text-yellow-500" />;
      default:
        return <Clock className="h-4 w-4 text-muted-foreground" />;
    }
  };

  const activeJobs = jobs.filter((j) => j.status === "queued" || j.status === "processing");

  return (
    <Card className="bg-card border-border">
      <CardHeader className="pb-3">
        <CardTitle className="text-lg flex items-center justify-between">
          <span>Job Queue</span>
          <div className="flex items-center gap-3 text-sm font-normal">
            <span className="flex items-center gap-1 text-muted-foreground">
              <Clock className="h-4 w-4" />~{formatTime(queueStats.averageWaitTime)} avg
            </span>
          </div>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Stats Row */}
        <div className="grid grid-cols-4 gap-2">
          <div className="text-center p-2 rounded-md bg-muted/50">
            <div className="text-2xl font-bold text-yellow-500">{queueStats.queued}</div>
            <div className="text-xs text-muted-foreground">Queued</div>
          </div>
          <div className="text-center p-2 rounded-md bg-muted/50">
            <div className="text-2xl font-bold text-primary">{queueStats.processing}</div>
            <div className="text-xs text-muted-foreground">Processing</div>
          </div>
          <div className="text-center p-2 rounded-md bg-muted/50">
            <div className="text-2xl font-bold text-green-500">{queueStats.completed}</div>
            <div className="text-xs text-muted-foreground">Completed</div>
          </div>
          <div className="text-center p-2 rounded-md bg-muted/50">
            <div className="text-2xl font-bold text-destructive">{queueStats.failed}</div>
            <div className="text-xs text-muted-foreground">Failed</div>
          </div>
        </div>

        {/* Estimated Wait */}
        {queueStats.queued > 0 && (
          <div className="p-3 rounded-md bg-primary/5 border border-primary/20">
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Estimated total wait</span>
              <span className="font-medium text-primary">
                {formatTime(queueStats.estimatedTotalWaitTime)}
              </span>
            </div>
          </div>
        )}

        {/* Active Jobs List */}
        {activeJobs.length > 0 && (
          <div className="space-y-2">
            <h4 className="text-sm font-medium text-muted-foreground">Active Jobs</h4>
            {activeJobs.slice(0, 3).map((job) => (
              <div key={job.id} className="flex items-center gap-3 p-2 rounded-md bg-muted/30">
                {getStatusIcon(job.status)}
                <div className="flex-1 min-w-0">
                  <div className="text-sm font-medium truncate">Job {job.id.slice(0, 8)}</div>
                  {job.status === "processing" && (
                    <Progress value={job.progress} className="h-1 mt-1" />
                  )}
                </div>
                <div
                  className={cn(
                    "text-xs px-2 py-0.5 rounded-full",
                    job.status === "processing"
                      ? "bg-primary/20 text-primary"
                      : "bg-yellow-500/20 text-yellow-500",
                  )}
                >
                  {job.status === "processing" ? `${job.progress}%` : "Queued"}
                </div>
              </div>
            ))}
            {activeJobs.length > 3 && (
              <p className="text-xs text-muted-foreground text-center">
                +{activeJobs.length - 3} more jobs
              </p>
            )}
          </div>
        )}

        {activeJobs.length === 0 && (
          <div className="text-center py-4 text-muted-foreground text-sm">
            No active jobs in queue
          </div>
        )}
      </CardContent>
    </Card>
  );
};
