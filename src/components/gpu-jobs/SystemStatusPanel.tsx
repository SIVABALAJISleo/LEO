import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { 
  Thermometer, 
  Cpu, 
  HardDrive, 
  Activity,
  Wifi,
  WifiOff,
  AlertTriangle,
  CheckCircle2,
  Zap
} from 'lucide-react';
import { useGpuJobs } from '@/hooks/useGpuJobs';
import { GPU_THERMAL_WARNING, GPU_THERMAL_CRITICAL } from '@/lib/gpuJobTypes';

export function SystemStatusPanel() {
  const { systemStatus, getMemoryReport, getThermalStatus } = useGpuJobs();
  const memoryReport = getMemoryReport();
  const thermalStatus = getThermalStatus();

  const memoryUsagePercent = memoryReport.total_mb > 0 
    ? (memoryReport.used_mb / memoryReport.total_mb) * 100 
    : 0;

  const gpuUtilization = systemStatus?.gpu_utilization_percent || 0;
  const cpuUtilization = systemStatus?.cpu_utilization_percent || 0;
  const isOnline = systemStatus?.is_online ?? true;

  const getTempColor = (temp: number) => {
    if (temp >= GPU_THERMAL_CRITICAL) return 'text-destructive';
    if (temp >= GPU_THERMAL_WARNING) return 'text-orange-500';
    return 'text-primary';
  };

  const getTempProgress = (temp: number) => {
    return Math.min((temp / 100) * 100, 100);
  };

  return (
    <Card className="bg-card border-border">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <Activity className="h-5 w-5 text-primary" />
              HYPER Engine Status
            </CardTitle>
            <CardDescription>Real-time GPU worker health monitoring</CardDescription>
          </div>
          <Badge variant={isOnline ? 'default' : 'destructive'} className="gap-1">
            {isOnline ? (
              <>
                <Wifi className="h-3 w-3" />
                Online
              </>
            ) : (
              <>
                <WifiOff className="h-3 w-3" />
                Offline
              </>
            )}
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Thermal Warning */}
        {!thermalStatus.is_safe && (
          <Alert variant="destructive">
            <AlertTriangle className="h-4 w-4" />
            <AlertTitle>Thermal Warning</AlertTitle>
            <AlertDescription>
              {thermalStatus.recommended_action === 'stop' 
                ? 'GPU temperature critical! Jobs will be paused for safety.'
                : 'GPU temperature elevated. Performance may be reduced.'}
            </AlertDescription>
          </Alert>
        )}

        {/* Memory Status */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <HardDrive className="h-4 w-4 text-muted-foreground" />
              <span className="text-sm font-medium">GPU Memory</span>
            </div>
            <span className="text-sm text-muted-foreground">
              {(memoryReport.used_mb / 1024).toFixed(1)}GB / {(memoryReport.total_mb / 1024).toFixed(1)}GB
            </span>
          </div>
          <Progress value={memoryUsagePercent} className="h-3" />
          <div className="flex items-center gap-2 text-xs text-muted-foreground">
            {memoryReport.can_accept_job ? (
              <>
                <CheckCircle2 className="h-3 w-3 text-primary" />
                Ready for new jobs (max: {(memoryReport.max_job_size_mb / 1024).toFixed(1)}GB)
              </>
            ) : (
              <>
                <AlertTriangle className="h-3 w-3 text-orange-500" />
                Memory low - wait for jobs to complete
              </>
            )}
          </div>
        </div>

        {/* GPU Temperature */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Thermometer className="h-4 w-4 text-muted-foreground" />
              <span className="text-sm font-medium">GPU Temperature</span>
            </div>
            <span className={`text-sm font-medium ${getTempColor(thermalStatus.gpu_temp)}`}>
              {thermalStatus.gpu_temp}°C
            </span>
          </div>
          <Progress 
            value={getTempProgress(thermalStatus.gpu_temp)} 
            className="h-3"
          />
          <div className="flex gap-4 text-xs text-muted-foreground">
            <span>Safe: &lt;{GPU_THERMAL_WARNING}°C</span>
            <span className="text-orange-500">Warning: {GPU_THERMAL_WARNING}-{GPU_THERMAL_CRITICAL}°C</span>
            <span className="text-destructive">Critical: &gt;{GPU_THERMAL_CRITICAL}°C</span>
          </div>
        </div>

        {/* CPU Temperature */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Cpu className="h-4 w-4 text-muted-foreground" />
              <span className="text-sm font-medium">CPU Temperature</span>
            </div>
            <span className={`text-sm font-medium ${getTempColor(thermalStatus.cpu_temp)}`}>
              {thermalStatus.cpu_temp}°C
            </span>
          </div>
          <Progress 
            value={getTempProgress(thermalStatus.cpu_temp)} 
            className="h-3"
          />
        </div>

        {/* GPU Utilization */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Zap className="h-4 w-4 text-muted-foreground" />
              <span className="text-sm font-medium">GPU Utilization</span>
            </div>
            <span className="text-sm text-muted-foreground">{gpuUtilization.toFixed(1)}%</span>
          </div>
          <Progress value={gpuUtilization} className="h-3" />
        </div>

        {/* CPU Utilization */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Cpu className="h-4 w-4 text-muted-foreground" />
              <span className="text-sm font-medium">CPU Utilization</span>
            </div>
            <span className="text-sm text-muted-foreground">{cpuUtilization.toFixed(1)}%</span>
          </div>
          <Progress value={cpuUtilization} className="h-3" />
        </div>

        {/* Worker Stats */}
        <div className="grid grid-cols-2 gap-4 pt-4 border-t border-border">
          <div className="text-center">
            <p className="text-2xl font-bold text-primary">
              {systemStatus?.jobs_completed_today || 0}
            </p>
            <p className="text-xs text-muted-foreground">Completed Today</p>
          </div>
          <div className="text-center">
            <p className="text-2xl font-bold text-destructive">
              {systemStatus?.jobs_failed_today || 0}
            </p>
            <p className="text-xs text-muted-foreground">Failed Today</p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
