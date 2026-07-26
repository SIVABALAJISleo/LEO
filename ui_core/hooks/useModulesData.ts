import { useState, useEffect, useCallback, useMemo } from "react";
import { firebaseClient as supabase } from "@/integrations/firebase/client";
import { useAuth } from "@/contexts/AuthContext";
import { useToast } from "@/hooks/use-toast";
import { Json } from "@/integrations/supabase/types";

export interface ModuleStatus {
  id: string;
  module_name: string;
  status: string;
  health_score: number | null;
  error_message: string | null;
  last_checked: string | null;
  current_job_id: string | null;
  metadata: Json | null;
}

export interface ModuleConfig {
  id: string;
  module_name: string;
  module_type: string;
  enabled: boolean;
  config: Json;
  settings: Json;
  speedup_achieved: number | null;
  compression_ratio_achieved: number | null;
}

export interface ModuleData {
  name: string;
  description: string;
  status: ModuleStatus | null;
  config: ModuleConfig | null;
}

export interface ModuleStats {
  totalRuns: number;
  successRate: number;
  avgLatencyImpact: number;
  performanceHistory: Array<{
    recorded_at: string;
    speedup: number;
    compression: number;
  }>;
  errorHistory: Array<{
    id: string;
    title: string;
    message: string;
    severity: string;
    created_at: string;
    resolved: boolean;
  }>;
}

const MODULE_DEFINITIONS: Record<string, string> = {
  Quantization:
    "Reduce model precision to INT8/FP16 for faster inference with minimal accuracy loss.",
  "Kernel Optimization": "Optimize CUDA kernels for maximum GPU utilization and throughput.",
  "Neural Approximation": "Replace expensive operations with learned approximations.",
  "Memory Compression": "Compress intermediate tensors to reduce memory footprint.",
  "Cache Optimization": "Intelligent caching of repeated computations and activations.",
  "Parallel Execution": "Execute independent operations concurrently on GPU streams.",
  "Distributed Computing": "Scale inference across multiple GPUs and nodes.",
  "Model Serving": "Optimized model loading and request batching for production.",
  "Streaming Inference": "Process data in streaming fashion for reduced latency.",
  "JIT Compilation": "Just-in-time compilation of model graphs for target hardware.",
  "Memory Management": "Advanced memory allocation and defragmentation strategies.",
  "Speculative Execution": "Predict and pre-compute likely execution paths.",
  "Adaptive Precision": "Dynamically adjust precision based on input characteristics.",
  "Graph Optimization": "Fuse operations and eliminate redundancies in computation graphs.",
  "Sparsity & Pruning": "Remove unnecessary weights and leverage sparse computation.",
};

export const MODULE_NAMES = Object.keys(MODULE_DEFINITIONS);

const DEFAULT_SETTINGS: Record<string, Json> = {
  Quantization: { precision: "INT8", calibration_samples: 1000, symmetric: true },
  "Kernel Optimization": { auto_tune: true, workspace_size_mb: 512, benchmark_iterations: 100 },
  "Neural Approximation": { approximation_level: "medium", error_threshold: 0.01 },
  "Memory Compression": { compression_algo: "lz4", compression_level: 3, min_tensor_size_kb: 64 },
  "Cache Optimization": { cache_size_mb: 1024, eviction_policy: "lru", prefetch_enabled: true },
  "Parallel Execution": { max_streams: 8, stream_priority: "high", sync_mode: "async" },
  "Distributed Computing": {
    num_workers: 4,
    communication_backend: "nccl",
    gradient_compression: true,
  },
  "Model Serving": { batch_size: 32, max_batch_delay_ms: 10, num_instances: 2 },
  "Streaming Inference": { chunk_size: 512, overlap_ratio: 0.1, buffer_size: 4 },
  "JIT Compilation": { optimization_level: 3, target_device: "cuda", cache_compiled: true },
  "Memory Management": {
    memory_pool_size_gb: 8,
    fragmentation_threshold: 0.3,
    gc_interval_ms: 1000,
  },
  "Speculative Execution": { speculation_depth: 3, confidence_threshold: 0.8, max_rollback: 2 },
  "Adaptive Precision": { min_precision: "FP16", max_precision: "FP32", adaptation_rate: 0.1 },
  "Graph Optimization": {
    fusion_enabled: true,
    constant_folding: true,
    dead_code_elimination: true,
  },
  "Sparsity & Pruning": { sparsity_target: 0.5, pruning_method: "magnitude", fine_tune_epochs: 5 },
};

export function useModulesData() {
  const { user } = useAuth();
  const { toast } = useToast();
  const [moduleStatuses, setModuleStatuses] = useState<ModuleStatus[]>([]);
  const [moduleConfigs, setModuleConfigs] = useState<ModuleConfig[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    if (!user) return;

    try {
      setLoading(true);
      setError(null);

      const [statusRes, configRes] = await Promise.all([
        supabase.from("module_status").select("*").eq("user_id", user.id),
        supabase.from("module_configs").select("*").eq("user_id", user.id),
      ]);

      if (statusRes.error) throw statusRes.error;
      if (configRes.error) throw configRes.error;

      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      setModuleStatuses((statusRes.data as any) || []);
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      setModuleConfigs((configRes.data as any) || []);
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
    } catch (err: any) {
      setError(err.message);
      console.error("Error fetching modules data:", err);
    } finally {
      setLoading(false);
    }
  }, [user]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  // Real-time subscriptions
  useEffect(() => {
    if (!user) return;

    const statusChannel = supabase
      .channel("module-status-changes")
      .on(
        "postgres_changes",
        {
          event: "*",
          schema: "public",
          table: "module_status",
          filter: `user_id=eq.${user.id}`,
        },
        () => fetchData(),
      )
      .subscribe();

    const configChannel = supabase
      .channel("module-config-changes")
      .on(
        "postgres_changes",
        {
          event: "*",
          schema: "public",
          table: "module_configs",
          filter: `user_id=eq.${user.id}`,
        },
        () => fetchData(),
      )
      .subscribe();

    return () => {
      supabase.removeChannel(statusChannel);
      supabase.removeChannel(configChannel);
    };
  }, [user, fetchData]);

  const modules = useMemo((): ModuleData[] => {
    return MODULE_NAMES.map((name) => ({
      name,
      description: MODULE_DEFINITIONS[name],
      status: moduleStatuses.find((s) => s.module_name === name) || null,
      config: moduleConfigs.find((c) => c.module_name === name) || null,
    }));
  }, [moduleStatuses, moduleConfigs]);

  const toggleModuleEnabled = async (moduleName: string, enabled: boolean) => {
    if (!user) return;

    try {
      const existingConfig = moduleConfigs.find((c) => c.module_name === moduleName);

      if (existingConfig) {
        const { error } = await supabase
          .from("module_configs")
          .update({ enabled, updated_at: new Date().toISOString() })
          .eq("id", existingConfig.id);

        if (error) throw error;
      } else {
        const { error } = await supabase.from("module_configs").insert({
          user_id: user.id,
          module_name: moduleName,
          module_type: "optimization",
          enabled,
          config: {},
          settings: DEFAULT_SETTINGS[moduleName] || {},
        });

        if (error) throw error;
      }

      toast({
        title: enabled ? "Module Enabled" : "Module Disabled",
        description: `${moduleName} has been ${enabled ? "enabled" : "disabled"}.`,
      });

      fetchData();
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
    } catch (err: any) {
      toast({
        title: "Error",
        description: err.message,
        variant: "destructive",
      });
    }
  };

  const updateModuleSettings = async (moduleName: string, settings: Json) => {
    if (!user) return;

    try {
      const existingConfig = moduleConfigs.find((c) => c.module_name === moduleName);

      if (existingConfig) {
        const { error } = await supabase
          .from("module_configs")
          .update({ settings, updated_at: new Date().toISOString() })
          .eq("id", existingConfig.id);

        if (error) throw error;
      } else {
        const { error } = await supabase.from("module_configs").insert({
          user_id: user.id,
          module_name: moduleName,
          module_type: "optimization",
          enabled: true,
          config: {},
          settings,
        });

        if (error) throw error;
      }

      toast({
        title: "Settings Saved",
        description: `${moduleName} settings have been updated.`,
      });

      fetchData();
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
    } catch (err: any) {
      toast({
        title: "Error",
        description: err.message,
        variant: "destructive",
      });
    }
  };

  const resetModuleSettings = async (moduleName: string) => {
    await updateModuleSettings(moduleName, DEFAULT_SETTINGS[moduleName] || {});
  };

  const batchToggleModules = async (moduleNames: string[], enabled: boolean) => {
    if (!user) return;

    try {
      for (const moduleName of moduleNames) {
        await toggleModuleEnabled(moduleName, enabled);
      }

      toast({
        title: "Batch Update Complete",
        description: `${moduleNames.length} modules have been ${enabled ? "enabled" : "disabled"}.`,
      });
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
    } catch (err: any) {
      toast({
        title: "Error",
        description: err.message,
        variant: "destructive",
      });
    }
  };

  const applySettingsTemplate = async (moduleNames: string[], template: Json) => {
    if (!user) return;

    try {
      for (const moduleName of moduleNames) {
        await updateModuleSettings(moduleName, template);
      }

      toast({
        title: "Template Applied",
        description: `Settings template applied to ${moduleNames.length} modules.`,
      });
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
    } catch (err: any) {
      toast({
        title: "Error",
        description: err.message,
        variant: "destructive",
      });
    }
  };

  const fetchModuleStats = async (moduleName: string): Promise<ModuleStats> => {
    if (!user) {
      return {
        totalRuns: 0,
        successRate: 0,
        avgLatencyImpact: 0,
        performanceHistory: [],
        errorHistory: [],
      };
    }

    try {
      const [metricsRes, alertsRes] = await Promise.all([
        supabase
          .from("performance_metrics")
          .select("*")
          .eq("user_id", user.id)
          .eq("module_name", moduleName)
          .order("recorded_at", { ascending: false })
          .limit(50),
        supabase
          .from("alerts")
          .select("*")
          .eq("user_id", user.id)
          .eq("module_name", moduleName)
          .order("created_at", { ascending: false })
          .limit(20),
      ]);

      const metrics = metricsRes.data || [];
      const alerts = alertsRes.data || [];

      const totalRuns = metrics.length;
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const successfulRuns = metrics.filter((m) => (m.metadata as any)?.success !== false).length;
      const successRate = totalRuns > 0 ? (successfulRuns / totalRuns) * 100 : 0;
      const avgLatencyImpact =
        metrics.length > 0
          ? metrics.reduce((sum, m) => sum + (m.latency_ms || 0), 0) / metrics.length
          : 0;

      const performanceHistory = metrics.map((m) => ({
        recorded_at: m.recorded_at,
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        speedup: (m.metadata as any)?.speedup || 1,
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        compression: (m.metadata as any)?.compression || 1,
      }));

      const errorHistory = alerts.map((a) => ({
        id: a.id,
        title: a.title,
        message: a.message,
        severity: a.severity,
        created_at: a.created_at,
        resolved: a.resolved,
      }));

      return {
        totalRuns,
        successRate,
        avgLatencyImpact,
        performanceHistory,
        errorHistory,
      };
    } catch (err) {
      console.error("Error fetching module stats:", err);
      return {
        totalRuns: 0,
        successRate: 0,
        avgLatencyImpact: 0,
        performanceHistory: [],
        errorHistory: [],
      };
    }
  };

  return {
    modules,
    moduleStatuses,
    moduleConfigs,
    loading,
    error,
    refetch: fetchData,
    toggleModuleEnabled,
    updateModuleSettings,
    resetModuleSettings,
    batchToggleModules,
    applySettingsTemplate,
    fetchModuleStats,
    getDefaultSettings: (name: string) => DEFAULT_SETTINGS[name] || {},
  };
}
