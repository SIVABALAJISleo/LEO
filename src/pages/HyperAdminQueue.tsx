import { useState, useEffect } from 'react';
import { supabase } from '@/integrations/supabase/client';
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
  HardDrive,
  Loader2,
  RefreshCw,
  Shield,
  ShieldAlert,
  Thermometer,
  Wifi,
  WifiOff,
  XCircle
} from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';
import { GpuJob, GpuSystemStatus, getStatusBadgeVariant, GPU_THERMAL_WARNING } from '@/lib/gpuJobTypes';
import { useAdminRole } from '@/hooks/useAdminRole';

export default function HyperAdminQueue() {
  const { isAdmin, isLoading: roleLoading } = useAdminRole();
  const [allJobs, setAllJobs] = useState<GpuJob[]>([]);
  const [systemStatus, setSystemStatus] = useState<GpuSystemStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const fetchData = async () => {
    try {
      // Fetch all jobs (admin view) - RLS will scope to user's own jobs for non-service role
      const { data: jobs } = await supabase
        .from('gpu_jobs')
        .select('*')
        .order('created_at', { ascending: false })
        .limit(100);

      const { data: status } = await supabase
        .from('gpu_system_status')
        .select('*')
        .order('last_heartbeat_at', { ascending: false })
        .limit(1)
        .single();

      setAllJobs((jobs || []) as unknown as GpuJob[]);
      setSystemStatus(status as unknown as GpuSystemStatus);
    } catch (err) {
      console.error('Admin fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // Only fetch data if user is admin
    if (isAdmin && !roleLoading) {
      fetchData();

      // Auto-refresh every 10 seconds
      const interval = setInterval(fetchData, 10000);
      return () => clearInterval(interval);
    }
  }, [isAdmin, roleLoading]);

  const handleRefresh = async () => {
    setRefreshing(true);
    await fetchData();
    setRefreshing(false);
  };

  // Show loading while checking admin role
  if (roleLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-background">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin text-primary mx-auto mb-4" />
          <p className="text-muted-foreground">Verifying access permissions...</p>
        </div>
      </div>
    );
  }

  // Redirect non-admin users with access denied message
  if (!isAdmin) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-background">
        <Card className="w-full max-w-md">
          <CardHeader className="text-center">
            <ShieldAlert className="w-16 h-16 mx-auto text-destructive mb-4" />
            <CardTitle>Access Denied</CardTitle>
            <CardDescription>
              You do not have permission to access this page. 
              Admin privileges are required.
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

  // Calculate stats
  const pendingJobs = allJobs.filter(j => j.status === 'pending' || j.status === 'queued');
  const runningJobs = allJobs.filter(j => j.status === 'running');
  const completedJobs = allJobs.filter(j => j.status === 'completed');
  const failedJobs = allJobs.filter(j => j.status === 'failed' || j.status === 'too_large');

  const isOnline = systemStatus?.is_online ?? false;
  const gpuTemp = systemStatus?.gpu_temperature_celsius ?? 0;
  const isThermalWarning = gpuTemp >= GPU_THERMAL_WARNING;

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-background">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <>

      <div className="min-h-screen bg-background p-6">
        <div className="max-w-7xl mx-auto space-y-6">
          {/* Header */}
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-primary">HYPER Admin Queue</h1>
              <p className="text-muted-foreground">
                Internal monitoring dashboard • Secret URL access only
              </p>
            </div>
            <div className="flex items-center gap-4">
              <Badge variant={isOnline ? 'default' : 'destructive'} className="gap-1">
                {isOnline ? <Wifi className="h-3 w-3" /> : <WifiOff className="h-3 w-3" />}
                Worker {isOnline ? 'Online' : 'Offline'}
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

          {/* Alerts */}
          {isThermalWarning && (
            <Alert variant="destructive">
              <Thermometer className="h-4 w-4" />
              <AlertTitle>Thermal Warning</AlertTitle>
              <AlertDescription>
                GPU temperature is {gpuTemp}°C. Jobs may be throttled or paused.
              </AlertDescription>
            </Alert>
          )}

          {!isOnline && (
            <Alert variant="destructive">
              <WifiOff className="h-4 w-4" />
              <AlertTitle>Worker Offline</AlertTitle>
              <AlertDescription>
                The HYPER worker is currently offline. Jobs are queued but not processing.
              </AlertDescription>
            </Alert>
          )}

          {/* Stats Cards */}
          <div className="grid gap-4 md:grid-cols-5">
            <Card className="bg-card border-border">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium flex items-center gap-2">
                  <Clock className="h-4 w-4" />
                  Queued
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{pendingJobs.length}</div>
              </CardContent>
            </Card>

            <Card className="bg-card border-border">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium flex items-center gap-2">
                  <Loader2 className="h-4 w-4" />
                  Running
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-primary">{runningJobs.length}</div>
              </CardContent>
            </Card>

            <Card className="bg-card border-border">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium flex items-center gap-2">
                  <CheckCircle2 className="h-4 w-4" />
                  Completed
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-green-500">{completedJobs.length}</div>
              </CardContent>
            </Card>

            <Card className="bg-card border-border">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium flex items-center gap-2">
                  <XCircle className="h-4 w-4" />
                  Failed
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-destructive">{failedJobs.length}</div>
              </CardContent>
            </Card>

            <Card className="bg-card border-border">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium flex items-center gap-2">
                  <Thermometer className="h-4 w-4" />
                  GPU Temp
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className={`text-2xl font-bold ${isThermalWarning ? 'text-orange-500' : 'text-primary'}`}>
                  {gpuTemp}°C
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Worker Health */}
          <Card className="bg-card border-border">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Activity className="h-5 w-5 text-primary" />
                Worker Health
              </CardTitle>
              <CardDescription>Real-time GPU worker status</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-4">
                <div>
                  <p className="text-sm text-muted-foreground mb-1">GPU Memory</p>
                  <Progress 
                    value={systemStatus?.gpu_memory_total_mb 
                      ? ((systemStatus?.gpu_memory_used_mb || 0) / systemStatus.gpu_memory_total_mb) * 100 
                      : 0
                    } 
                    className="h-3"
                  />
                  <p className="text-xs text-muted-foreground mt-1">
                    {((systemStatus?.gpu_memory_used_mb || 0) / 1024).toFixed(1)}GB / 
                    {((systemStatus?.gpu_memory_total_mb || 0) / 1024).toFixed(0)}GB
                  </p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground mb-1">GPU Utilization</p>
                  <Progress value={systemStatus?.gpu_utilization_percent || 0} className="h-3" />
                  <p className="text-xs text-muted-foreground mt-1">
                    {(systemStatus?.gpu_utilization_percent || 0).toFixed(1)}%
                  </p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground mb-1">CPU Utilization</p>
                  <Progress value={systemStatus?.cpu_utilization_percent || 0} className="h-3" />
                  <p className="text-xs text-muted-foreground mt-1">
                    {(systemStatus?.cpu_utilization_percent || 0).toFixed(1)}%
                  </p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground mb-1">Last Heartbeat</p>
                  <p className="text-sm">
                    {systemStatus?.last_heartbeat_at 
                      ? formatDistanceToNow(new Date(systemStatus.last_heartbeat_at), { addSuffix: true })
                      : 'Never'
                    }
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Job Tables */}
          <Tabs defaultValue="all" className="space-y-4">
            <TabsList>
              <TabsTrigger value="all">All Jobs ({allJobs.length})</TabsTrigger>
              <TabsTrigger value="running">Running ({runningJobs.length})</TabsTrigger>
              <TabsTrigger value="failed">Failed ({failedJobs.length})</TabsTrigger>
            </TabsList>

            <TabsContent value="all">
              <Card className="bg-card border-border">
                <CardContent className="p-0">
                  <ScrollArea className="h-[400px]">
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>ID</TableHead>
                          <TableHead>Type</TableHead>
                          <TableHead>Status</TableHead>
                          <TableHead>Progress</TableHead>
                          <TableHead>Memory</TableHead>
                          <TableHead>Created</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {allJobs.map(job => (
                          <TableRow key={job.id}>
                            <TableCell className="font-mono text-xs">
                              {job.id.slice(0, 8)}...
                            </TableCell>
                            <TableCell>{job.job_type}</TableCell>
                            <TableCell>
                              <Badge variant={getStatusBadgeVariant(job.status)}>
                                {job.status}
                              </Badge>
                            </TableCell>
                            <TableCell>
                              {job.status === 'running' && (
                                <Progress value={job.progress} className="h-2 w-20" />
                              )}
                              {job.status !== 'running' && '-'}
                            </TableCell>
                            <TableCell>
                              {((job.memory_required_mb || 0) / 1024).toFixed(1)}GB
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
            </TabsContent>

            <TabsContent value="running">
              <Card className="bg-card border-border">
                <CardContent className="p-4">
                  {runningJobs.length === 0 ? (
                    <p className="text-center text-muted-foreground py-8">
                      No running jobs
                    </p>
                  ) : (
                    <div className="space-y-4">
                      {runningJobs.map(job => (
                        <div key={job.id} className="p-4 border border-border rounded-lg">
                          <div className="flex justify-between mb-2">
                            <span className="font-medium">{job.job_name || job.job_type}</span>
                            <span className="text-sm text-muted-foreground">
                              {job.progress}%
                            </span>
                          </div>
                          <Progress value={job.progress} className="h-3" />
                          {job.thermal_paused && (
                            <Badge variant="outline" className="mt-2 text-orange-500">
                              Thermal Paused
                            </Badge>
                          )}
                        </div>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="failed">
              <Card className="bg-card border-border">
                <CardContent className="p-4">
                  {failedJobs.length === 0 ? (
                    <p className="text-center text-muted-foreground py-8">
                      No failed jobs
                    </p>
                  ) : (
                    <div className="space-y-4">
                      {failedJobs.map(job => (
                        <div key={job.id} className="p-4 border border-destructive/30 rounded-lg bg-destructive/5">
                          <div className="flex justify-between mb-2">
                            <span className="font-medium">{job.job_name || job.job_type}</span>
                            <Badge variant="destructive">{job.status}</Badge>
                          </div>
                          {job.error_message && (
                            <p className="text-sm text-destructive">{job.error_message}</p>
                          )}
                        </div>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>

          {/* Safety Status */}
          <Card className="bg-card border-border">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Shield className="h-5 w-5 text-primary" />
                GPU Safety Warnings
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-3">
                <div className={`p-4 rounded-lg ${isThermalWarning ? 'bg-orange-500/10 border border-orange-500/30' : 'bg-primary/10 border border-primary/30'}`}>
                  <div className="flex items-center gap-2 mb-2">
                    <Thermometer className={`h-5 w-5 ${isThermalWarning ? 'text-orange-500' : 'text-primary'}`} />
                    <span className="font-medium">Thermal</span>
                  </div>
                  <p className="text-sm text-muted-foreground">
                    {isThermalWarning 
                      ? `Warning: ${gpuTemp}°C exceeds safe threshold` 
                      : 'All temperatures normal'
                    }
                  </p>
                </div>
                <div className="p-4 rounded-lg bg-primary/10 border border-primary/30">
                  <div className="flex items-center gap-2 mb-2">
                    <HardDrive className="h-5 w-5 text-primary" />
                    <span className="font-medium">Memory</span>
                  </div>
                  <p className="text-sm text-muted-foreground">
                    {((systemStatus?.gpu_memory_total_mb || 0) - (systemStatus?.gpu_memory_used_mb || 0)) / 1024 > 2
                      ? 'Sufficient memory available'
                      : 'Warning: Low GPU memory'
                    }
                  </p>
                </div>
                <div className={`p-4 rounded-lg ${isOnline ? 'bg-primary/10 border border-primary/30' : 'bg-destructive/10 border border-destructive/30'}`}>
                  <div className="flex items-center gap-2 mb-2">
                    {isOnline ? <Wifi className="h-5 w-5 text-primary" /> : <WifiOff className="h-5 w-5 text-destructive" />}
                    <span className="font-medium">Connectivity</span>
                  </div>
                  <p className="text-sm text-muted-foreground">
                    {isOnline 
                      ? 'Worker connected and processing' 
                      : 'Worker offline - jobs queued locally'
                    }
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </>
  );
}
