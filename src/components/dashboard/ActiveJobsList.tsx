import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { InferenceJob } from '@/lib/types';
import { Briefcase, Clock, Loader2 } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';
import { cn } from '@/lib/utils';

interface ActiveJobsListProps {
  jobs: InferenceJob[];
}

export const ActiveJobsList = ({ jobs }: ActiveJobsListProps) => {
  const getStatusConfig = (status: string) => {
    switch (status) {
      case 'running':
        return { className: 'bg-primary/20 text-primary', icon: Loader2 };
      case 'queued':
        return { className: 'bg-yellow-500/20 text-yellow-500', icon: Clock };
      default:
        return { className: 'bg-muted text-muted-foreground', icon: Clock };
    }
  };

  return (
    <Card className="p-6 bg-card border-border">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold">Active Jobs</h3>
        <Badge variant="secondary">{jobs.length} active</Badge>
      </div>

      {jobs.length === 0 ? (
        <div className="text-center py-8 text-muted-foreground">
          <Briefcase className="h-8 w-8 mx-auto mb-2 opacity-50" />
          <p className="text-sm">No active jobs</p>
        </div>
      ) : (
        <div className="space-y-3 max-h-[300px] overflow-y-auto">
          {jobs.map((job) => {
            const statusConfig = getStatusConfig(job.status);
            const StatusIcon = statusConfig.icon;
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
            const modelName = (job as any).models?.name || 'Unknown Model';
            const modules = Array.isArray(job.enabled_modules) 
              ? job.enabled_modules 
              : [];

            return (
              <div
                key={job.id}
                className="p-4 rounded-lg bg-muted/30 border border-border hover:border-primary/50 transition-colors"
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="flex-1 min-w-0">
                    <h4 className="font-medium truncate">{modelName}</h4>
                    <p className="text-xs text-muted-foreground">
                      Started {formatDistanceToNow(new Date(job.created_at), { addSuffix: true })}
                    </p>
                  </div>
                  <Badge className={cn('ml-2 flex items-center gap-1', statusConfig.className)}>
                    <StatusIcon className={cn('h-3 w-3', job.status === 'running' && 'animate-spin')} />
                    {job.status}
                  </Badge>
                </div>

                {/* Progress bar for running jobs */}
                {job.status === 'running' && (
                  <div className="mb-2">
                    <div className="flex justify-between text-xs text-muted-foreground mb-1">
                      <span>Progress</span>
                      <span>{job.progress || 0}%</span>
                    </div>
                    <div className="h-1.5 bg-muted rounded-full overflow-hidden">
                      <div
                        className="h-full bg-primary transition-all duration-500"
                        style={{ width: `${job.progress || 0}%` }}
                      />
                    </div>
                  </div>
                )}

                {/* Modules used */}
                {modules.length > 0 && (
                  <div className="flex flex-wrap gap-1 mt-2">
                    {modules.slice(0, 3).map((module) => (
                      <Badge key={module} variant="outline" className="text-xs">
                        {module.replace(/_/g, ' ')}
                      </Badge>
                    ))}
                    {modules.length > 3 && (
                      <Badge variant="outline" className="text-xs">
                        +{modules.length - 3} more
                      </Badge>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </Card>
  );
};
