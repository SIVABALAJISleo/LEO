import { useState, useEffect } from 'react';
import { firebaseClient as supabase } from '@/integrations/firebase/client';
import { useAuth } from '@/contexts/AuthContext';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Activity,
  AlertTriangle,
  CheckCircle2,
  Clock,
  Cpu,
  Database,
  Loader2,
  RefreshCw,
  Server,
  Shield,
  Thermometer,
  TrendingUp,
  Wifi,
  WifiOff,
  Zap
} from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';
import { useAdminRole } from '@/hooks/useAdminRole';

interface AdminSummary {
  stats: {
    total_jobs: number;
    pending: number;
    queued: number;
    running: number;
    completed: number;
    failed: number;
    cancelled: number;
    by_tier: {
      light: number;
      medium: number;
      heavy: number;
    };
  };
  queue_depth: number;
  avg_runtime_ms: number;
  avg_runtime_formatted: string;
  active_workers: Array<{
    worker_id: string;
    gpu_temp_celsius: number;
    is_processing: boolean;
    current_job_id: string | null;
  }>;
  registered_agents: Array<{
    id: string;
    agent_name: string;
    is_active: boolean;
    last_used_at: string;
  }>;
  timestamp: string;
}

interface JobData {
  id: string;
  job_type: string;
  job_tier: string | null;
  status: string;
  progress: number;
  memory_required_mb: number | null;
  created_at: string;
  started_at: string | null;
  completed_at: string | null;
  error_message: string | null;
  worker_id: string | null;
}

export default function SecretAdminPage() {
  const { user } = useAuth();
  const { isAdmin, isLoading: roleLoading } = useAdminRole();
  const [summary, setSummary] = useState<AdminSummary | null>(null);
  const [jobs, setJobs] = useState<JobData[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const fetchData = async () => {
    try {
      // Fetch all jobs for admin view
      const { data: jobsData } = await supabase
        .from('gpu_jobs')
        .select('*')
        .order('created_at', { ascending: false })
        .limit(200);

      setJobs((jobsData || []) as JobData[]);

      // Calculate summary locally since we can access all jobs as admin
      const allJobs = (jobsData || []) as JobData[];
      const localSummary: AdminSummary = {
        stats: {
          total_jobs: allJobs.length,
          pending: allJobs.filter((j: JobData) => j.status === 'pending').length,
          queued: allJobs.filter((j: JobData) => j.status === 'queued').length,
          running: allJobs.filter((j: JobData) => j.status === 'running').length,
          completed: allJobs.filter((j: JobData) => j.status === 'completed').length,
          failed: allJobs.filter((j: JobData) => j.status === 'failed').length,
          cancelled: allJobs.filter((j: JobData) => j.status === 'cancelled').length,
          by_tier: {
            light: allJobs.filter((j: JobData) => j.job_tier === 'light').length,
            medium: allJobs.filter((j: JobData) => j.job_tier === 'medium').length,
            heavy: allJobs.filter((j: JobData) => j.job_tier === 'heavy').length,
          },
        },
        queue_depth: allJobs.filter((j: JobData) => j.status === 'queued').length,
        avg_runtime_ms: 0,
        avg_runtime_formatted: '0s',
        active_workers: [],
        registered_agents: [],
        timestamp: new Date().toISOString(),
      };

      // Calculate average runtime
      const completedJobs = allJobs.filter((j: JobData) =>
        j.status === 'completed' && j.started_at && j.completed_at
      );
      if (completedJobs.length > 0) {
        const totalMs = completedJobs.reduce((acc: number, j: JobData) => {
          return acc + (new Date(j.completed_at!).getTime() - new Date(j.started_at!).getTime());
        }, 0);
        localSummary.avg_runtime_ms = Math.round(totalMs / completedJobs.length);
        localSummary.avg_runtime_formatted = formatDuration(localSummary.avg_runtime_ms);
      }

      // Get system status for worker info
      const { data: systemStatus } = await supabase
        .from('gpu_system_status')
        .select('*')
        .order('last_heartbeat_at', { ascending: false })
        .limit(5);

      if (systemStatus && systemStatus.length > 0) {
        localSummary.active_workers = systemStatus.map((s: any) => ({
          worker_id: s.worker_id,
          gpu_temp_celsius: s.gpu_temperature_celsius || 0,
          is_processing: s.active_job_id !== null,
          current_job_id: s.active_job_id,
        }));
      }

      setSummary(localSummary);
    } catch (err) {
      console.error('Error fetching admin data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isAdmin && !roleLoading) {
      fetchData();
      const interval = setInterval(fetchData, 15000);
      return () => clearInterval(interval);
    }
  }, [isAdmin, roleLoading]);

  const handleRefresh = async () => {
    setRefreshing(true);
    await fetchData();
    setRefreshing(false);
  };

  if (roleLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-background">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin text-primary mx-auto mb-4" />
          <p className="text-muted-foreground">Verifying access...</p>
        </div>
      </div>
    );
  }

  if (!isAdmin) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-background">
        <Card className="w-full max-w-md">
          <CardHeader className="text-center">
            <Shield className="w-16 h-16 mx-auto text-destructive mb-4" />
            <CardTitle>Access Denied</CardTitle>
            <CardDescription>
              This page requires admin privileges.
            </CardDescription>
          </CardHeader>
          <CardContent className="text-center">
            <Button onClick={() => window.location.href = '/dashboard'}>
              Return to Dashboard
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-background">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  const stats = summary?.stats;

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="p-3 rounded-lg bg-primary/10">
              <Zap className="h-8 w-8 text-primary" />
            </div>
            <div>
              <h1 className="text-3xl font-bold">
                <span className="text-primary">HYPER</span> Secret Admin
              </h1>
              <p className="text-muted-foreground text-sm">
                Internal monitoring • Not linked anywhere
              </p>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <Badge variant="outline" className="gap-1">
              <Database className="h-3 w-3" />
              {stats?.total_jobs || 0} Total Jobs
            </Badge>
            <Button
              variant="outline"
              size="sm"
              onClick={handleRefresh}
              disabled={refreshing}
            >
              <RefreshCw className={`h-4 w-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
          </div>
        </div>

        {/* Stats Overview */}
        <div className="grid gap-4 md:grid-cols-6">
          <Card className="bg-gradient-to-br from-primary/10 to-transparent border-primary/20">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <Clock className="h-4 w-4" />
                Queue
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-primary">{summary?.queue_depth || 0}</div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <Loader2 className="h-4 w-4" />
                Running
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-blue-500">{stats?.running || 0}</div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <CheckCircle2 className="h-4 w-4" />
                Completed
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-500">{stats?.completed || 0}</div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <AlertTriangle className="h-4 w-4" />
                Failed
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-destructive">{stats?.failed || 0}</div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <TrendingUp className="h-4 w-4" />
                Avg Runtime
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{summary?.avg_runtime_formatted || '-'}</div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <Server className="h-4 w-4" />
                Workers
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-primary">
                {summary?.active_workers?.length || 0}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Job Tier Breakdown */}
        <div className="grid gap-4 md:grid-cols-3">
          <Card className="border-green-500/30 bg-green-500/5">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Light Jobs</CardTitle>
              <CardDescription>Instant server-side processing</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-green-500">{stats?.by_tier?.light || 0}</div>
            </CardContent>
          </Card>

          <Card className="border-yellow-500/30 bg-yellow-500/5">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Medium Jobs</CardTitle>
              <CardDescription>Client-side WebGPU/WASM</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-yellow-500">{stats?.by_tier?.medium || 0}</div>
            </CardContent>
          </Card>

          <Card className="border-red-500/30 bg-red-500/5">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Heavy Jobs</CardTitle>
              <CardDescription>Laptop GPU agent required</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-red-500">{stats?.by_tier?.heavy || 0}</div>
            </CardContent>
          </Card>
        </div>

        {/* Active Workers */}
        {summary?.active_workers && summary.active_workers.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Activity className="h-5 w-5 text-primary" />
                Active Workers
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {summary.active_workers.map((worker, idx) => (
                  <Card key={idx} className="bg-muted/30">
                    <CardContent className="pt-4">
                      <div className="flex items-center justify-between mb-2">
                        <span className="font-mono text-sm">{worker.worker_id}</span>
                        <Badge variant={worker.is_processing ? 'default' : 'secondary'}>
                          {worker.is_processing ? 'Processing' : 'Idle'}
                        </Badge>
                      </div>
                      <div className="flex items-center gap-2 text-sm text-muted-foreground">
                        <Thermometer className="h-4 w-4" />
                        <span>{worker.gpu_temp_celsius}°C</span>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Jobs Table */}
        <Tabs defaultValue="all" className="space-y-4">
          <TabsList>
            <TabsTrigger value="all">All ({jobs.length})</TabsTrigger>
            <TabsTrigger value="running">Running ({jobs.filter(j => j.status === 'running').length})</TabsTrigger>
            <TabsTrigger value="queued">Queued ({jobs.filter(j => j.status === 'queued').length})</TabsTrigger>
            <TabsTrigger value="failed">Failed ({jobs.filter(j => j.status === 'failed').length})</TabsTrigger>
          </TabsList>

          <TabsContent value="all">
            <JobsTable jobs={jobs} />
          </TabsContent>

          <TabsContent value="running">
            <JobsTable jobs={jobs.filter(j => j.status === 'running')} />
          </TabsContent>

          <TabsContent value="queued">
            <JobsTable jobs={jobs.filter(j => j.status === 'queued')} />
          </TabsContent>

          <TabsContent value="failed">
            <JobsTable jobs={jobs.filter(j => j.status === 'failed')} />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}

function JobsTable({ jobs }: { jobs: JobData[] }) {
  if (jobs.length === 0) {
    return (
      <Card>
        <CardContent className="py-12 text-center text-muted-foreground">
          No jobs found
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardContent className="p-0">
        <ScrollArea className="h-[500px]">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>ID</TableHead>
                <TableHead>Type</TableHead>
                <TableHead>Tier</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Progress</TableHead>
                <TableHead>Memory</TableHead>
                <TableHead>Created</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {jobs.map(job => (
                <TableRow key={job.id}>
                  <TableCell className="font-mono text-xs">
                    {job.id.slice(0, 8)}...
                  </TableCell>
                  <TableCell>{job.job_type}</TableCell>
                  <TableCell>
                    <Badge variant={
                      job.job_tier === 'light' ? 'outline' :
                        job.job_tier === 'medium' ? 'secondary' : 'default'
                    }>
                      {job.job_tier}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <Badge variant={
                      job.status === 'completed' ? 'default' :
                        job.status === 'failed' ? 'destructive' :
                          job.status === 'running' ? 'default' : 'secondary'
                    } className={
                      job.status === 'running' ? 'bg-blue-500' :
                        job.status === 'completed' ? 'bg-green-500' : ''
                    }>
                      {job.status}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    {job.status === 'running' ? (
                      <Progress value={job.progress} className="h-2 w-20" />
                    ) : job.status === 'completed' ? (
                      '100%'
                    ) : (
                      '-'
                    )}
                  </TableCell>
                  <TableCell>
                    {job.memory_required_mb
                      ? `${(job.memory_required_mb / 1024).toFixed(1)}GB`
                      : '-'
                    }
                  </TableCell>
                  <TableCell className="text-xs text-muted-foreground">
                    {formatDistanceToNow(new Date(job.created_at), { addSuffix: true })}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </ScrollArea>
      </CardContent>
    </Card>
  );
}

function formatDuration(ms: number): string {
  if (ms < 1000) return `${ms}ms`;
  if (ms < 60000) return `${(ms / 1000).toFixed(1)}s`;
  if (ms < 3600000) return `${(ms / 60000).toFixed(1)}m`;
  return `${(ms / 3600000).toFixed(1)}h`;
}
