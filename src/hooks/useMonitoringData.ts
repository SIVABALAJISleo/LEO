import { useState, useEffect, useCallback } from 'react';
import { supabase } from '@/integrations/supabase/client';
import { useAuth } from '@/contexts/AuthContext';

export interface PerformanceMetric {
  id: string;
  metric_name: string;
  metric_value: number;
  latency_ms: number | null;
  throughput_rps: number | null;
  cache_hit_ratio: number | null;
  cpu_usage_percent: number | null;
  memory_mb: number | null;
  module_name: string | null;
  recorded_at: string;
}

export interface SystemMetric {
  id: string;
  gpu_utilization: number | null;
  memory_usage: number | null;
  cpu_percent: number | null;
  disk_gb: number | null;
  temperature: number | null;
  power_draw: number | null;
  throughput: number | null;
  active_jobs: number | null;
  total_requests: number | null;
  status: string | null;
  recorded_at: string;
}

export interface Alert {
  id: string;
  title: string;
  message: string;
  severity: string;
  alert_type: string;
  module_name: string | null;
  resolved: boolean;
  created_at: string;
}

export interface ModuleConfig {
  id: string;
  module_name: string;
  module_type: string;
  enabled: boolean;
  speedup_achieved: number | null;
  compression_ratio_achieved: number | null;
}

export function useMonitoringData() {
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [performanceMetrics, setPerformanceMetrics] = useState<PerformanceMetric[]>([]);
  const [systemMetrics, setSystemMetrics] = useState<SystemMetric[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [moduleConfigs, setModuleConfigs] = useState<ModuleConfig[]>([]);
  const [dateRange, setDateRange] = useState<{ start: Date; end: Date }>({
    start: new Date(Date.now() - 24 * 60 * 60 * 1000),
    end: new Date()
  });

  const fetchPerformanceMetrics = useCallback(async () => {
    if (!user) return;
    
    const { data, error } = await supabase
      .from('performance_metrics')
      .select('*')
      .eq('user_id', user.id)
      .gte('recorded_at', dateRange.start.toISOString())
      .lte('recorded_at', dateRange.end.toISOString())
      .order('recorded_at', { ascending: false })
      .limit(500);

    if (error) throw error;
    setPerformanceMetrics(data || []);
  }, [user, dateRange]);

  const fetchSystemMetrics = useCallback(async () => {
    if (!user) return;

    const { data, error } = await supabase
      .from('system_metrics')
      .select('*')
      .eq('user_id', user.id)
      .gte('recorded_at', dateRange.start.toISOString())
      .lte('recorded_at', dateRange.end.toISOString())
      .order('recorded_at', { ascending: false })
      .limit(100);

    if (error) throw error;
    setSystemMetrics(data || []);
  }, [user, dateRange]);

  const fetchAlerts = useCallback(async () => {
    if (!user) return;

    const { data, error } = await supabase
      .from('alerts')
      .select('*')
      .eq('user_id', user.id)
      .order('created_at', { ascending: false })
      .limit(100);

    if (error) throw error;
    setAlerts(data || []);
  }, [user]);

  const fetchModuleConfigs = useCallback(async () => {
    if (!user) return;

    const { data, error } = await supabase
      .from('module_configs')
      .select('*')
      .eq('user_id', user.id);

    if (error) throw error;
    setModuleConfigs(data || []);
  }, [user]);

  const refreshAll = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      await Promise.all([
        fetchPerformanceMetrics(),
        fetchSystemMetrics(),
        fetchAlerts(),
        fetchModuleConfigs()
      ]);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [fetchPerformanceMetrics, fetchSystemMetrics, fetchAlerts, fetchModuleConfigs]);

  const resolveAlert = async (alertId: string) => {
    if (!user) return;

    const { error } = await supabase
      .from('alerts')
      .update({ resolved: true, resolved_at: new Date().toISOString() })
      .eq('id', alertId)
      .eq('user_id', user.id);

    if (error) throw error;
    await fetchAlerts();
  };

  useEffect(() => {
    refreshAll();
  }, [refreshAll]);

  // Real-time subscriptions
  useEffect(() => {
    if (!user) return;

    const channel = supabase
      .channel('monitoring-updates')
      .on('postgres_changes', { event: '*', schema: 'public', table: 'performance_metrics', filter: `user_id=eq.${user.id}` }, () => fetchPerformanceMetrics())
      .on('postgres_changes', { event: '*', schema: 'public', table: 'system_metrics', filter: `user_id=eq.${user.id}` }, () => fetchSystemMetrics())
      .on('postgres_changes', { event: '*', schema: 'public', table: 'alerts', filter: `user_id=eq.${user.id}` }, () => fetchAlerts())
      .subscribe();

    return () => {
      supabase.removeChannel(channel);
    };
  }, [user, fetchPerformanceMetrics, fetchSystemMetrics, fetchAlerts]);

  // Calculate KPIs
  const kpis = {
    avgLatency: performanceMetrics.length > 0
      ? performanceMetrics.reduce((sum, m) => sum + (m.latency_ms || 0), 0) / performanceMetrics.filter(m => m.latency_ms).length || 0
      : 0,
    avgThroughput: performanceMetrics.length > 0
      ? performanceMetrics.reduce((sum, m) => sum + (m.throughput_rps || 0), 0) / performanceMetrics.filter(m => m.throughput_rps).length || 0
      : 0,
    avgCacheHit: performanceMetrics.length > 0
      ? performanceMetrics.reduce((sum, m) => sum + (m.cache_hit_ratio || 0), 0) / performanceMetrics.filter(m => m.cache_hit_ratio).length || 0
      : 0,
    activeModules: moduleConfigs.filter(m => m.enabled).length
  };

  return {
    loading,
    error,
    performanceMetrics,
    systemMetrics,
    alerts,
    moduleConfigs,
    kpis,
    dateRange,
    setDateRange,
    refreshAll,
    resolveAlert
  };
}
