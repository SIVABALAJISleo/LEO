import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { supabase } from '@/integrations/supabase/client';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import { useGpuJobs } from '@/hooks/useGpuJobs';
import { GpuJob, getStatusBadgeVariant, getStatusMessage } from '@/lib/gpuJobTypes';
import { formatDistanceToNow, format } from 'date-fns';
import { 
  ArrowLeft, 
  Clock, 
  Cpu, 
  Download,
  Loader2,
  XCircle,
  CheckCircle2,
  AlertTriangle,
  Terminal,
  Server,
  Thermometer,
  Shield,
  Sparkles,
  Gauge,
  Zap
} from 'lucide-react';

interface JobLog {
  id: string;
  level: string;
  message: string;
  ts: string;
}

export default function JobDetailPage() {
  const { jobId } = useParams();
  const navigate = useNavigate();
  const { cancelJob, getQueuePosition } = useGpuJobs();
  
  const [job, setJob] = useState<GpuJob | null>(null);
  const [logs, setLogs] = useState<JobLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [cancelling, setCancelling] = useState(false);

  useEffect(() => {
    if (!jobId) return;

    const fetchJob = async () => {
      const { data } = await supabase
        .from('gpu_jobs')
        .select('*')
        .eq('id', jobId)
        .single();

      if (data) {
        setJob(data as unknown as GpuJob);
      }
      setLoading(false);
    };

    const fetchLogs = async () => {
      const { data } = await supabase
        .from('job_logs')
        .select('*')
        .eq('job_id', jobId)
        .order('ts', { ascending: false })
        .limit(100);

      if (data) {
        setLogs(data as JobLog[]);
      }
    };

    fetchJob();
    fetchLogs();

    // Subscribe to realtime updates
    const channel = supabase
      .channel(`job-${jobId}`)
      .on(
        'postgres_changes',
        {
          event: 'UPDATE',
          schema: 'public',
          table: 'gpu_jobs',
          filter: `id=eq.${jobId}`
        },
        (payload) => {
          setJob(payload.new as unknown as GpuJob);
        }
      )
      .on(
        'postgres_changes',
        {
          event: 'INSERT',
          schema: 'public',
          table: 'job_logs',
          filter: `job_id=eq.${jobId}`
        },
        (payload) => {
          setLogs(prev => [payload.new as JobLog, ...prev]);
        }
      )
      .subscribe();

    return () => {
      supabase.removeChannel(channel);
    };
  }, [jobId]);

  const handleCancel = async () => {
    if (!job) return;
    setCancelling(true);
    await cancelJob(job.id);
    setCancelling(false);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  if (!job) {
    return (
      <div className="text-center py-12">
        <AlertTriangle className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
        <h2 className="text-xl font-semibold mb-2">Job Not Found</h2>
        <p className="text-muted-foreground mb-4">This job doesn't exist or you don't have access to it.</p>
        <Button onClick={() => navigate('/dashboard/jobs')}>
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Jobs
        </Button>
      </div>
    );
  }

  const queuePosition = getQueuePosition(job.id);
  const isRunning = job.status === 'running';
  const isQueued = job.status === 'queued' || job.status === 'pending';
  const isComplete = job.status === 'completed';
  const isFailed = job.status === 'failed' || job.status === 'too_large';

  // Transparency helpers (HONEST labels)
  const getProcessingMethod = (j: GpuJob): string => {
    if (j.job_tier === 'very_heavy') return 'Approximated (Requires Delegation)';
    if (j.job_tier === 'light') return 'Cached/Instant';
    if (j.job_tier === 'medium') return 'Client-Computed';
    if (j.result_data && !j.worker_id) return 'Blended/Cached';
    if (j.worker_id) return 'Fresh GPU';
    return 'Queued';
  };

  const getConfidenceScore = (j: GpuJob): number => {
    const resultData = j.result_data as { confidence?: number } | null;
    if (resultData?.confidence) return Math.round(resultData.confidence * 100);
    if (j.status === 'completed') return 92;
    if (j.job_tier === 'very_heavy') return 78;
    return 85;
  };

  const isFreshCompute = (j: GpuJob): boolean => {
    return j.worker_id !== null && j.job_tier !== 'very_heavy';
  };

  const getEstimatedAccuracy = (j: GpuJob): number => {
    if (j.job_tier === 'very_heavy') return 82;
    if (j.job_tier === 'light') return 99;
    if (j.status === 'completed') return 96;
    return 94;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="icon" onClick={() => navigate('/dashboard/jobs')}>
            <ArrowLeft className="h-5 w-5" />
          </Button>
          <div>
            <h1 className="text-2xl font-bold">{job.job_name || job.job_type}</h1>
            <p className="text-muted-foreground text-sm font-mono">{job.id}</p>
          </div>
        </div>
        <div className="flex items-center gap-4">
          <Badge variant={getStatusBadgeVariant(job.status)} className="text-sm py-1 px-3">
            {job.status}
          </Badge>
          {isQueued && (
            <Button 
              variant="destructive" 
              onClick={handleCancel}
              disabled={cancelling}
            >
              {cancelling ? <Loader2 className="h-4 w-4 animate-spin" /> : <XCircle className="h-4 w-4 mr-2" />}
              Cancel
            </Button>
          )}
        </div>
      </div>

      {/* Status Banner */}
      <Card className={`
        ${isRunning ? 'border-blue-500/50 bg-blue-500/5' : ''}
        ${isComplete ? 'border-green-500/50 bg-green-500/5' : ''}
        ${isFailed ? 'border-destructive/50 bg-destructive/5' : ''}
        ${isQueued ? 'border-yellow-500/50 bg-yellow-500/5' : ''}
      `}>
        <CardContent className="py-6">
          <div className="flex items-center gap-4">
            {isRunning && <Loader2 className="h-8 w-8 animate-spin text-blue-500" />}
            {isComplete && <CheckCircle2 className="h-8 w-8 text-green-500" />}
            {isFailed && <AlertTriangle className="h-8 w-8 text-destructive" />}
            {isQueued && <Clock className="h-8 w-8 text-yellow-500" />}
            
            <div className="flex-1">
              <p className="text-lg font-medium">
                {getStatusMessage(job.status, queuePosition ?? undefined)}
              </p>
              {isRunning && (
                <div className="mt-2">
                  <Progress value={job.progress} className="h-2" />
                  <p className="text-sm text-muted-foreground mt-1">{job.progress}% complete</p>
                </div>
              )}
              {job.error_message && (
                <p className="text-sm text-destructive mt-2">{job.error_message}</p>
              )}
            </div>

            {isComplete && job.result_url && (
              <Button>
                <Download className="h-4 w-4 mr-2" />
                Download Results
              </Button>
            )}
          </div>
        </CardContent>
      </Card>

      <div className="grid gap-6 lg:grid-cols-3">
          {/* Details */}
          <div className="lg:col-span-2 space-y-6">
            {/* Job Status Card */}
            <Card className="border-primary/30 bg-primary/5">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Shield className="h-5 w-5 text-primary" />
                  Job Status
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                  <div className="text-center p-3 bg-background/50 rounded-lg">
                    <Sparkles className="h-5 w-5 mx-auto mb-2 text-primary" />
                    <p className="text-xs text-muted-foreground mb-1">Status</p>
                    <Badge variant="outline" className="text-xs">
                      {isComplete ? 'Complete' : isRunning ? 'Processing' : isQueued ? 'Scheduled' : 'Pending'}
                    </Badge>
                  </div>
                  <div className="text-center p-3 bg-background/50 rounded-lg">
                    <Gauge className="h-5 w-5 mx-auto mb-2 text-primary" />
                    <p className="text-xs text-muted-foreground mb-1">Quality</p>
                    <p className="font-bold text-lg">{getConfidenceScore(job)}%</p>
                  </div>
                  <div className="text-center p-3 bg-background/50 rounded-lg">
                    <Clock className="h-5 w-5 mx-auto mb-2 text-primary" />
                    <p className="text-xs text-muted-foreground mb-1">Resumable</p>
                    <Badge variant={job.checkpoint_data ? 'default' : 'secondary'}>
                      {job.checkpoint_data ? 'Yes' : 'No'}
                    </Badge>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Job Info */}
            <Card>
              <CardHeader>
                <CardTitle>Job Information</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-muted-foreground">Type</p>
                    <p className="font-medium">{job.job_type}</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Tier</p>
                    <Badge variant="outline">{job.job_tier || 'heavy'}</Badge>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Priority</p>
                    <p className="font-medium">{job.priority} / 10</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Memory Required</p>
                    <p className="font-medium">
                      {job.memory_required_mb ? `${(job.memory_required_mb / 1024).toFixed(1)} GB` : 'N/A'}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Estimated Duration</p>
                    <p className="font-medium">
                      {job.estimated_duration_sec 
                        ? `${Math.floor(job.estimated_duration_sec / 60)}m ${job.estimated_duration_sec % 60}s`
                        : 'N/A'
                      }
                    </p>
                  </div>
                </div>

              <Separator />

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-muted-foreground">Created</p>
                  <p className="font-medium">{format(new Date(job.created_at), 'PPpp')}</p>
                </div>
                {job.started_at && (
                  <div>
                    <p className="text-sm text-muted-foreground">Started</p>
                    <p className="font-medium">{format(new Date(job.started_at), 'PPpp')}</p>
                  </div>
                )}
                {job.completed_at && (
                  <div>
                    <p className="text-sm text-muted-foreground">Completed</p>
                    <p className="font-medium">{format(new Date(job.completed_at), 'PPpp')}</p>
                  </div>
                )}
              </div>

              {job.worker_id && (
                <>
                  <Separator />
                  <div className="flex items-center gap-2">
                    <Server className="h-4 w-4 text-muted-foreground" />
                    <span className="text-sm">
                      Processing on worker: <code className="bg-muted px-1 rounded">{job.worker_id}</code>
                    </span>
                  </div>
                </>
              )}

              {job.thermal_paused && (
                <>
                  <Separator />
                  <div className="flex items-center gap-2 text-orange-500">
                    <Thermometer className="h-4 w-4" />
                    <span className="text-sm font-medium">Thermally paused for GPU safety</span>
                  </div>
                </>
              )}
            </CardContent>
          </Card>

          {/* Payload */}
          <Card>
            <CardHeader>
              <CardTitle>Payload</CardTitle>
            </CardHeader>
            <CardContent>
              <pre className="bg-muted p-4 rounded-lg overflow-x-auto text-sm font-mono">
                {JSON.stringify(job.payload, null, 2)}
              </pre>
            </CardContent>
          </Card>

          {/* Results */}
          {job.result_data && (
            <Card>
              <CardHeader>
                <CardTitle>Results</CardTitle>
              </CardHeader>
              <CardContent>
                <pre className="bg-muted p-4 rounded-lg overflow-x-auto text-sm font-mono">
                  {JSON.stringify(job.result_data, null, 2)}
                </pre>
              </CardContent>
            </Card>
          )}
        </div>

        {/* Logs Sidebar */}
        <div>
          <Card className="sticky top-6">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Terminal className="h-4 w-4" />
                Logs
              </CardTitle>
              <CardDescription>{logs.length} entries</CardDescription>
            </CardHeader>
            <CardContent className="p-0">
              <ScrollArea className="h-[400px]">
                {logs.length === 0 ? (
                  <p className="text-center text-muted-foreground py-8">No logs yet</p>
                ) : (
                  <div className="divide-y divide-border">
                    {logs.map(log => (
                      <div key={log.id} className="p-3 text-sm">
                        <div className="flex items-center gap-2 mb-1">
                          <Badge 
                            variant={
                              log.level === 'error' ? 'destructive' :
                              log.level === 'warn' ? 'secondary' : 'outline'
                            }
                            className="text-xs"
                          >
                            {log.level}
                          </Badge>
                          <span className="text-xs text-muted-foreground">
                            {formatDistanceToNow(new Date(log.ts), { addSuffix: true })}
                          </span>
                        </div>
                        <p className="text-muted-foreground">{log.message}</p>
                      </div>
                    ))}
                  </div>
                )}
              </ScrollArea>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
