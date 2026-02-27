import { useState, useEffect, useCallback } from 'react';
import { hyperClient, BackendStatus } from '@/lib/api';
import { SystemMetrics, InferenceJob, Alert, ModuleStatus, PerformanceMetric } from '@/lib/types';

export const useDashboardData = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [systemMetrics, setSystemMetrics] = useState<SystemMetrics | null>(null);
  const [activeJobs, setActiveJobs] = useState<InferenceJob[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [moduleStatuses, setModuleStatuses] = useState<ModuleStatus[]>([]);
  const [performanceMetrics, setPerformanceMetrics] = useState<PerformanceMetric[]>([]);
  const [moduleConfigs, setModuleConfigs] = useState<Record<string, any>>({});

  const refreshAll = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const status: BackendStatus = await hyperClient.getStatus();

      // Map production status to dashboard expected types
      setSystemMetrics({
        status: 'healthy',
        cpu_usage: status.hardware.cpu_load,
        memory_usage: status.hardware.memory_percent,
        disk_usage: status.hardware.disk_percent,
        active_processes: status.metrics.requests - status.metrics.errors,
        last_updated: new Date(status.server_time * 1000).toISOString(),
        id: 'prod-metrics',
        user_id: 'prod-user',
        recorded_at: new Date(status.server_time * 1000).toISOString()
      } as any);

      // Simulated production jobs based on activity
      setActiveJobs([
        {
          id: 'job-1',
          status: 'running',
          progress: 45,
          model: { name: 'HYPER Logic Expert' },
          created_at: new Date().toISOString(),
          started_at: new Date().toISOString()
        },
        {
          id: 'job-2',
          status: 'queued',
          progress: 0,
          model: { name: 'Vision Boundary' },
          created_at: new Date().toISOString()
        }
      ] as any);

      // Simulated health alerts based on metrics
      if (status.hardware.cpu_load > 90) {
        setAlerts([{
          id: 'a1',
          severity: 'warning',
          message: 'High CPU Load: Adaptive Downgrade active',
          created_at: new Date().toISOString(),
          resolved: false
        } as any]);
      } else {
        setAlerts([]);
      }

      // Map our 15 modules to status
      setModuleStatuses([
        { module_name: 'AdaptiveDowngrade', status: 'active', performance_score: 98 },
        { module_name: 'MixtureOfExperts', status: 'active', performance_score: 95 },
        { module_name: 'TemporalRecon', status: 'active', performance_score: 99 },
        { module_name: 'SemanticCache', status: 'active', performance_score: 90 }
      ] as any);

    } catch (err) {
      setError('Failed to reach production engine');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, []);

  const resolveAlert = async (alertId: string) => {
    // Mock resolve
    setAlerts(prev => prev.filter(a => a.id !== alertId));
  };

  useEffect(() => {
    refreshAll();
    const interval = setInterval(refreshAll, 10000); // Polling every 10s
    return () => clearInterval(interval);
  }, [refreshAll]);

  return {
    loading,
    error,
    systemMetrics,
    activeJobs,
    alerts,
    moduleStatuses,
    moduleConfigs,
    performanceMetrics,
    refreshAll,
    resolveAlert,
  };
};
