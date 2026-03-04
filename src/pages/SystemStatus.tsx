import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { firebaseClient as supabase } from '@/integrations/firebase/client';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import {
  Activity,
  ArrowLeft,
  CheckCircle2,
  Cpu,
  HardDrive,
  Loader2,
  RefreshCw,
  Shield,
  Thermometer,
  Wifi,
  WifiOff,
  Zap
} from 'lucide-react';
import { GpuSystemStatus, GPU_THERMAL_WARNING, GPU_THERMAL_CRITICAL, GPU_MEMORY_LIMIT_MB } from '@/lib/gpuJobTypes';
import { hyperClient, BackendStatus } from '@/lib/api';

export default function SystemStatus() {
  const [systemStatus, setSystemStatus] = useState<GpuSystemStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [jobCounts, setJobCounts] = useState({ pending: 0, running: 0 });
  const [backendStatus, setBackendStatus] = useState<BackendStatus | null>(null);

  const fetchStatus = async () => {
    try {
      const { data: status } = await supabase
        .from('gpu_system_status')
        .select('*')
        .order('last_heartbeat_at', { ascending: false })
        .limit(1)
        .single();

      // Get job counts
      const { count: pendingCount } = await supabase
        .from('gpu_jobs')
        .select('*', { count: 'exact', head: true })
        .in('status', ['pending', 'queued']);

      const { count: runningCount } = await supabase
        .from('gpu_jobs')
        .select('*', { count: 'exact', head: true })
        .eq('status', 'running');

      setSystemStatus(status as unknown as GpuSystemStatus);
      setJobCounts({
        pending: pendingCount || 0,
        running: runningCount || 0
      });

      // Fetch Real-time Backend Orchestration Status
      try {
        const bStatus = await hyperClient.getStatus();
        setBackendStatus(bStatus);
      // eslint-disable-next-line @typescript-eslint/no-unused-vars
      } catch (err) {
        console.warn('Backend server not reachable on port 8005. Falling back to mock data.');
      }
    } catch (err) {
      console.error('Error fetching system status:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStatus();

    // Subscribe to realtime updates
    const channel = supabase
      .channel('system-status-public')
      .on(
        'postgres_changes',
        {
          event: '*',
          schema: 'public',
          table: 'gpu_system_status'
        },
        () => {
          fetchStatus();
        }
      )
      .subscribe();

    // Auto-refresh every 30 seconds
    const interval = setInterval(fetchStatus, 30000);

    return () => {
      supabase.removeChannel(channel);
      clearInterval(interval);
    };
  }, []);

  const handleRefresh = async () => {
    setRefreshing(true);
    await fetchStatus();
    setRefreshing(false);
  };

  // Calculate values
  const gpuTemp = systemStatus?.gpu_temperature_celsius ?? 45;
  const cpuTemp = systemStatus?.cpu_temperature_celsius ?? 50;
  const gpuMemUsed = systemStatus?.gpu_memory_used_mb ?? 0;
  const gpuMemTotal = systemStatus?.gpu_memory_total_mb ?? GPU_MEMORY_LIMIT_MB;
  const gpuUtil = systemStatus?.gpu_utilization_percent ?? 0;
  const cpuUtil = systemStatus?.cpu_utilization_percent ?? 0;
  const isOnline = systemStatus?.is_online ?? true;
  const isThrottled = systemStatus?.is_thermal_throttled ?? false;

  const isTempWarning = gpuTemp >= GPU_THERMAL_WARNING || cpuTemp >= GPU_THERMAL_WARNING;
  const isTempCritical = gpuTemp >= GPU_THERMAL_CRITICAL || cpuTemp >= GPU_THERMAL_CRITICAL;

  const getTempColor = (temp: number) => {
    if (temp >= GPU_THERMAL_CRITICAL) return 'text-destructive';
    if (temp >= GPU_THERMAL_WARNING) return 'text-orange-500';
    return 'text-primary';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-background">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <>

      <div className="min-h-screen bg-background">
        {/* Header */}
        <header className="border-b border-border bg-card/50 backdrop-blur-sm sticky top-0 z-50">
          <div className="container mx-auto px-4 py-4 flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Link to="/">
                <Button variant="ghost" size="sm">
                  <ArrowLeft className="h-4 w-4 mr-2" />
                  Back
                </Button>
              </Link>
              <div>
                <h1 className="text-xl font-bold text-primary">HYPER System Status</h1>
                <p className="text-sm text-muted-foreground">Real-time GPU engine monitoring</p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <Badge variant={isOnline ? 'default' : 'destructive'} className="gap-1">
                {isOnline ? <Wifi className="h-3 w-3" /> : <WifiOff className="h-3 w-3" />}
                {isOnline ? 'Online' : 'Offline'}
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
        </header>

        <main className="container mx-auto px-4 py-8 space-y-6">
          {/* Alerts */}
          {isTempCritical && (
            <Alert variant="destructive">
              <Thermometer className="h-4 w-4" />
              <AlertTitle>Critical Temperature</AlertTitle>
              <AlertDescription>
                GPU or CPU temperature is critically high. Jobs are paused for hardware safety.
              </AlertDescription>
            </Alert>
          )}

          {isTempWarning && !isTempCritical && (
            <Alert className="border-orange-500/30 bg-orange-500/10">
              <Thermometer className="h-4 w-4 text-orange-500" />
              <AlertTitle className="text-orange-500">Elevated Temperature</AlertTitle>
              <AlertDescription>
                Temperature is above normal. Performance may be reduced.
              </AlertDescription>
            </Alert>
          )}

          {/* Quick Stats */}
          <div className="grid gap-4 md:grid-cols-5">
            <Card className="bg-card border-border">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium flex items-center gap-2">
                  <Activity className="h-4 w-4 text-primary" />
                  Status
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center gap-2">
                  {isOnline ? (
                    <>
                      <CheckCircle2 className="h-5 w-5 text-primary" />
                      <span className="text-lg font-bold text-primary">Operational</span>
                    </>
                  ) : (
                    <>
                      <WifiOff className="h-5 w-5 text-destructive" />
                      <span className="text-lg font-bold text-destructive">Offline</span>
                    </>
                  )}
                </div>
              </CardContent>
            </Card>

            <Card className="bg-card border-border">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium flex items-center gap-2">
                  <Loader2 className="h-4 w-4 text-muted-foreground" />
                  Queue
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{jobCounts.pending}</div>
                <p className="text-xs text-muted-foreground">{jobCounts.running} running</p>
              </CardContent>
            </Card>

            <Card className="bg-card border-border">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium flex items-center gap-2">
                  <Thermometer className={`h-4 w-4 ${getTempColor(gpuTemp)}`} />
                  GPU Temp
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className={`text-2xl font-bold ${getTempColor(gpuTemp)}`}>
                  {gpuTemp}°C
                </div>
                <p className="text-xs text-muted-foreground">
                  {isTempCritical ? 'Critical' : isTempWarning ? 'Elevated' : 'Normal'}
                </p>
              </CardContent>
            </Card>

            <Card className="bg-card border-border">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium flex items-center gap-2">
                  <HardDrive className="h-4 w-4 text-muted-foreground" />
                  GPU Memory
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {(gpuMemUsed / 1024).toFixed(1)}GB
                </div>
                <p className="text-xs text-muted-foreground">
                  of {(gpuMemTotal / 1024).toFixed(0)}GB used
                </p>
              </CardContent>
            </Card>
            <Card className="bg-card border-border">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium flex items-center gap-2">
                  <Activity className="h-4 w-4 text-primary" />
                  Orchestration
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {backendStatus?.version || "1.0.0-cpu"}
                </div>
                <p className="text-xs text-muted-foreground">
                  {backendStatus ? `${backendStatus.metrics.requests} requests handled` : "Connecting to engine..."}
                </p>
              </CardContent>
            </Card>
          </div>

          {/* Detailed Status */}
          <div className="grid gap-6 lg:grid-cols-2">
            <Card className="bg-card border-border">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Zap className="h-5 w-5 text-primary" />
                  GPU Metrics
                </CardTitle>
                <CardDescription>Real-time GPU performance data</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Temperature</span>
                    <span className={getTempColor(gpuTemp)}>{gpuTemp}°C</span>
                  </div>
                  <Progress value={(gpuTemp / 100) * 100} className="h-3" />
                </div>

                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Memory Usage</span>
                    <span>{(gpuMemUsed / 1024).toFixed(1)}GB / {(gpuMemTotal / 1024).toFixed(0)}GB</span>
                  </div>
                  <Progress value={(gpuMemUsed / gpuMemTotal) * 100} className="h-3" />
                </div>

                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Utilization</span>
                    <span>{gpuUtil.toFixed(1)}%</span>
                  </div>
                  <Progress value={gpuUtil} className="h-3" />
                </div>

                {isThrottled && (
                  <Badge variant="outline" className="text-orange-500 border-orange-500">
                    Thermal Throttling Active
                  </Badge>
                )}
              </CardContent>
            </Card>

            <Card className="bg-card border-border">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Cpu className="h-5 w-5 text-primary" />
                  CPU Metrics
                </CardTitle>
                <CardDescription>System CPU performance data</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Temperature</span>
                    <span className={getTempColor(cpuTemp)}>{cpuTemp}°C</span>
                  </div>
                  <Progress value={(cpuTemp / 100) * 100} className="h-3" />
                </div>

                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Utilization</span>
                    <span>{cpuUtil.toFixed(1)}%</span>
                  </div>
                  <Progress value={cpuUtil} className="h-3" />
                </div>

                <div className="pt-4 border-t border-border">
                  <p className="text-sm text-muted-foreground">
                    Jobs completed today: <span className="font-medium text-foreground">{systemStatus?.jobs_completed_today || 0}</span>
                  </p>
                  <p className="text-sm text-muted-foreground mt-1">
                    Jobs failed today: <span className="font-medium text-destructive">{systemStatus?.jobs_failed_today || 0}</span>
                  </p>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Safety Features */}
          <Card className="bg-card border-border">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Shield className="h-5 w-5 text-primary" />
                Safety Features
              </CardTitle>
              <CardDescription>
                HYPER protects your hardware with multiple safety layers
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-3">
                <div className="p-4 rounded-lg bg-primary/10 border border-primary/30">
                  <CheckCircle2 className="h-6 w-6 text-primary mb-2" />
                  <h4 className="font-medium">Memory Protection</h4>
                  <p className="text-sm text-muted-foreground mt-1">
                    Jobs exceeding available memory are rejected safely
                  </p>
                </div>
                <div className="p-4 rounded-lg bg-primary/10 border border-primary/30">
                  <CheckCircle2 className="h-6 w-6 text-primary mb-2" />
                  <h4 className="font-medium">Thermal Guard</h4>
                  <p className="text-sm text-muted-foreground mt-1">
                    Auto-pauses jobs when temperature exceeds safe limits
                  </p>
                </div>
                <div className="p-4 rounded-lg bg-primary/10 border border-primary/30">
                  <CheckCircle2 className="h-6 w-6 text-primary mb-2" />
                  <h4 className="font-medium">Offline Resilience</h4>
                  <p className="text-sm text-muted-foreground mt-1">
                    Checkpoints preserve progress during network disruptions
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </main>
      </div>
    </>
  );
}
