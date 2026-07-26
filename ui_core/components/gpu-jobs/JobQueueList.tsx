import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Clock,
  Download,
  XCircle,
  AlertTriangle,
  CheckCircle2,
  Loader2,
  Pause,
  ListOrdered,
} from "lucide-react";
import { useGpuJobs } from "@/hooks/useGpuJobs";
import { GpuJob, getStatusBadgeVariant, getStatusMessage, getStatusColor } from "@/lib/gpuJobTypes";
import { formatDistanceToNow } from "date-fns";

function JobCard({
  job,
  position,
  onCancel,
}: {
  job: GpuJob;
  position: number | null;
  onCancel: (id: string) => void;
}) {
  const statusMessage = getStatusMessage(job.status, position || undefined);
  const statusColor = getStatusColor(job.status);
  const canCancel = job.status === "pending" || job.status === "queued";

  const getStatusIcon = () => {
    switch (job.status) {
      case "pending":
      case "queued":
        return <Clock className="h-4 w-4" />;
      case "running":
        return <Loader2 className="h-4 w-4 animate-spin" />;
      case "paused":
        return <Pause className="h-4 w-4" />;
      case "completed":
        return <CheckCircle2 className="h-4 w-4" />;
      case "failed":
      case "too_large":
        return <AlertTriangle className="h-4 w-4" />;
      default:
        return <XCircle className="h-4 w-4" />;
    }
  };

  return (
    <div className="p-4 border border-border rounded-lg bg-card/50 hover:bg-card/80 transition-colors">
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <h4 className="font-medium truncate">{job.job_name || job.job_type}</h4>
            <Badge variant={getStatusBadgeVariant(job.status)} className="shrink-0">
              <span className={`flex items-center gap-1 ${statusColor}`}>
                {getStatusIcon()}
                {job.status}
              </span>
            </Badge>
          </div>

          <p className="text-sm text-muted-foreground mb-2">{statusMessage}</p>

          <div className="flex flex-wrap gap-x-4 gap-y-1 text-xs text-muted-foreground">
            <span>Type: {job.job_type}</span>
            <span>Memory: {((job.memory_required_mb || 0) / 1024).toFixed(1)}GB</span>
            <span>
              Created: {formatDistanceToNow(new Date(job.created_at), { addSuffix: true })}
            </span>
          </div>

          {job.status === "running" && (
            <div className="mt-3">
              <div className="flex justify-between text-xs mb-1">
                <span>Progress</span>
                <span>{job.progress}%</span>
              </div>
              <Progress value={job.progress} className="h-2" />
            </div>
          )}

          {job.error_message && (
            <div className="mt-2 p-2 bg-destructive/10 border border-destructive/30 rounded text-sm text-destructive">
              {job.error_message}
            </div>
          )}

          {job.thermal_paused && (
            <div className="mt-2 p-2 bg-orange-500/10 border border-orange-500/30 rounded text-sm text-orange-500">
              Job paused due to thermal protection. Will resume when temperature normalizes.
            </div>
          )}
        </div>

        <div className="flex flex-col gap-2 shrink-0">
          {canCancel && (
            <Button
              size="sm"
              variant="outline"
              onClick={() => onCancel(job.id)}
              className="text-destructive hover:text-destructive"
            >
              <XCircle className="h-4 w-4 mr-1" />
              Cancel
            </Button>
          )}

          {job.status === "completed" && job.result_url && (
            <Button size="sm" asChild>
              <a href={job.result_url} target="_blank" rel="noopener noreferrer">
                <Download className="h-4 w-4 mr-1" />
                Download
              </a>
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}

export function JobQueueList() {
  const { jobs, loading, cancelJob, getQueuePosition, getJobStats } = useGpuJobs();
  const stats = getJobStats();

  if (loading) {
    return (
      <Card className="bg-card border-border">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <ListOrdered className="h-5 w-5 text-primary" />
            Your Job Queue
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {[1, 2, 3].map((i) => (
            <Skeleton key={i} className="h-24 w-full" />
          ))}
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="bg-card border-border">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <ListOrdered className="h-5 w-5 text-primary" />
              Your Job Queue
            </CardTitle>
            <CardDescription>
              {stats.total} total jobs • {stats.pending} queued • {stats.running} running
            </CardDescription>
          </div>
          <div className="flex gap-2">
            <Badge variant="secondary">{stats.completed} completed</Badge>
            {stats.failed > 0 && <Badge variant="destructive">{stats.failed} failed</Badge>}
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {jobs.length === 0 ? (
          <div className="text-center py-8 text-muted-foreground">
            <ListOrdered className="h-12 w-12 mx-auto mb-4 opacity-50" />
            <p>No jobs yet. Create your first GPU job above!</p>
          </div>
        ) : (
          <ScrollArea className="h-[500px] pr-4">
            <div className="space-y-3">
              {jobs.map((job) => (
                <JobCard
                  key={job.id}
                  job={job}
                  position={getQueuePosition(job.id)}
                  onCancel={cancelJob}
                />
              ))}
            </div>
          </ScrollArea>
        )}
      </CardContent>
    </Card>
  );
}
