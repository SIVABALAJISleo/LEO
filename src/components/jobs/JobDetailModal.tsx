import { Clock, Zap, HardDrive, Cpu, Calendar, CheckCircle, XCircle, RotateCcw } from 'lucide-react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Separator } from '@/components/ui/separator';
import { ScrollArea } from '@/components/ui/scroll-area';
import { InferenceJob } from '@/hooks/useJobsData';
import { cn } from '@/lib/utils';
import { format, formatDistanceToNow } from 'date-fns';

interface JobDetailModalProps {
  job: InferenceJob | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onCancel: () => void;
  onRetry: () => void;
}

export function JobDetailModal({ job, open, onOpenChange, onCancel, onRetry }: JobDetailModalProps) {
  if (!job) return null;

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'completed':
        return 'bg-green-500/20 text-green-400 border-green-500/30';
      case 'running':
        return 'bg-blue-500/20 text-blue-400 border-blue-500/30';
      case 'queued':
        return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30';
      case 'failed':
        return 'bg-red-500/20 text-red-400 border-red-500/30';
      case 'cancelled':
        return 'bg-muted text-muted-foreground border-border';
      default:
        return 'bg-muted text-muted-foreground border-border';
    }
  };

  const enabledModules = Array.isArray(job.enabled_modules) ? job.enabled_modules : [];
  const inputData = typeof job.input_data === 'object' && job.input_data !== null ? job.input_data as Record<string, any> : {};
  const outputData = typeof job.output_data === 'object' && job.output_data !== null ? job.output_data as Record<string, any> : null;
  const optimizationOptions = typeof job.optimization_options === 'object' && job.optimization_options !== null ? job.optimization_options as Record<string, any> : {};

  const getDuration = () => {
    if (!job.started_at) return null;
    const start = new Date(job.started_at);
    const end = job.completed_at ? new Date(job.completed_at) : new Date();
    const diffMs = end.getTime() - start.getTime();
    const diffSec = Math.floor(diffMs / 1000);
    if (diffSec < 60) return `${diffSec}s`;
    const diffMin = Math.floor(diffSec / 60);
    const remSec = diffSec % 60;
    return `${diffMin}m ${remSec}s`;
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-3xl max-h-[90vh]">
        <DialogHeader>
          <div className="flex items-center gap-3">
            <DialogTitle>Job Details</DialogTitle>
            <Badge variant="outline" className={cn("text-xs", getStatusColor(job.status))}>
              {job.status}
            </Badge>
          </div>
          <DialogDescription className="font-mono text-xs">
            ID: {job.id}
          </DialogDescription>
        </DialogHeader>

        <ScrollArea className="max-h-[60vh] pr-4">
          <div className="space-y-6">
            {/* Progress for running jobs */}
            {job.status === 'running' && (
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Progress</span>
                  <span className="font-medium">{job.progress || 0}%</span>
                </div>
                <Progress value={job.progress || 0} className="h-2" />
              </div>
            )}

            {/* Error message */}
            {job.error_message && (
              <div className="p-4 bg-red-500/10 border border-red-500/30 rounded-lg">
                <div className="flex items-center gap-2 text-red-400 mb-2">
                  <XCircle className="h-4 w-4" />
                  <span className="font-medium">Error</span>
                </div>
                <p className="text-sm text-red-300">{job.error_message}</p>
              </div>
            )}

            {/* Performance Metrics */}
            {(job.latency_ms || job.speedup || job.compression_ratio) && (
              <>
                <div className="grid grid-cols-3 gap-4">
                  {job.latency_ms && (
                    <div className="p-4 bg-card rounded-lg border border-border text-center">
                      <Clock className="h-5 w-5 mx-auto mb-2 text-muted-foreground" />
                      <p className="text-xs text-muted-foreground">Latency</p>
                      <p className="text-lg font-bold">{job.latency_ms} ms</p>
                    </div>
                  )}
                  {job.speedup && (
                    <div className="p-4 bg-card rounded-lg border border-border text-center">
                      <Zap className="h-5 w-5 mx-auto mb-2 text-primary" />
                      <p className="text-xs text-muted-foreground">Speedup</p>
                      <p className="text-lg font-bold">{job.speedup.toFixed(2)}x</p>
                    </div>
                  )}
                  {job.compression_ratio && (
                    <div className="p-4 bg-card rounded-lg border border-border text-center">
                      <HardDrive className="h-5 w-5 mx-auto mb-2 text-primary" />
                      <p className="text-xs text-muted-foreground">Compression</p>
                      <p className="text-lg font-bold">{job.compression_ratio.toFixed(2)}x</p>
                    </div>
                  )}
                </div>
                <Separator />
              </>
            )}

            {/* Model & Timestamps */}
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-3">
                <h4 className="text-sm font-semibold flex items-center gap-2">
                  <Cpu className="h-4 w-4" />
                  Model
                </h4>
                <div className="p-3 bg-muted/50 rounded-lg">
                  <p className="font-medium">{job.model?.name || 'Unknown'}</p>
                  <p className="text-xs text-muted-foreground">{job.model?.model_type}</p>
                </div>
              </div>
              <div className="space-y-3">
                <h4 className="text-sm font-semibold flex items-center gap-2">
                  <Calendar className="h-4 w-4" />
                  Timeline
                </h4>
                <div className="space-y-1 text-sm">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Created:</span>
                    <span>{format(new Date(job.created_at), 'MMM d, yyyy HH:mm')}</span>
                  </div>
                  {job.started_at && (
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Started:</span>
                      <span>{format(new Date(job.started_at), 'HH:mm:ss')}</span>
                    </div>
                  )}
                  {job.completed_at && (
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Completed:</span>
                      <span>{format(new Date(job.completed_at), 'HH:mm:ss')}</span>
                    </div>
                  )}
                  {getDuration() && (
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Duration:</span>
                      <span className="font-medium">{getDuration()}</span>
                    </div>
                  )}
                </div>
              </div>
            </div>

            <Separator />

            {/* Enabled Modules */}
            <div className="space-y-3">
              <h4 className="text-sm font-semibold">Enabled Modules ({enabledModules.length})</h4>
              {enabledModules.length > 0 ? (
                <div className="flex flex-wrap gap-2">
                  {enabledModules.map((module, i) => (
                    <Badge key={i} variant="secondary">
                      {String(module)}
                    </Badge>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-muted-foreground">No optimization modules enabled</p>
              )}
            </div>

            <Separator />

            {/* Input Data */}
            <div className="space-y-3">
              <h4 className="text-sm font-semibold">Input Data</h4>
              <pre className="p-3 bg-muted/50 rounded-lg text-xs overflow-x-auto">
                {JSON.stringify(inputData, null, 2)}
              </pre>
            </div>

            {/* Output Data */}
            {outputData && (
              <div className="space-y-3">
                <h4 className="text-sm font-semibold">Output Data</h4>
                <pre className="p-3 bg-muted/50 rounded-lg text-xs overflow-x-auto">
                  {JSON.stringify(outputData, null, 2)}
                </pre>
              </div>
            )}

            {/* Optimization Options */}
            {Object.keys(optimizationOptions).length > 0 && (
              <div className="space-y-3">
                <h4 className="text-sm font-semibold">Optimization Options</h4>
                <pre className="p-3 bg-muted/50 rounded-lg text-xs overflow-x-auto">
                  {JSON.stringify(optimizationOptions, null, 2)}
                </pre>
              </div>
            )}
          </div>
        </ScrollArea>

        <DialogFooter className="flex gap-2 sm:gap-0">
          {(job.status === 'queued' || job.status === 'running') && (
            <Button
              variant="outline"
              onClick={onCancel}
              className="text-red-400 border-red-500/30 hover:bg-red-500/10"
            >
              <XCircle className="h-4 w-4 mr-2" />
              Cancel Job
            </Button>
          )}
          {(job.status === 'failed' || job.status === 'cancelled') && (
            <Button variant="outline" onClick={onRetry}>
              <RotateCcw className="h-4 w-4 mr-2" />
              Retry Job
            </Button>
          )}
          <Button onClick={() => onOpenChange(false)}>Close</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
