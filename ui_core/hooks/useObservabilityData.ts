import { useState, useEffect } from "react";
import { firebaseClient as supabase } from "@/integrations/firebase/client";
import { useAuth } from "@/contexts/AuthContext";
import { toast } from "sonner";

export function useObservabilityData() {
  const { user } = useAuth();
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [metricsRaw, setMetricsRaw] = useState<any[]>([]);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [metricsAggregated, setMetricsAggregated] = useState<any[]>([]);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [traces, setTraces] = useState<any[]>([]);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [anomalies, setAnomalies] = useState<any[]>([]);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [correlations, setCorrelations] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (user) fetchAll();
  }, [user]);

  const fetchAll = async () => {
    setIsLoading(true);
    const [rawRes, aggRes, tracesRes, anomaliesRes, corrRes] = await Promise.all([
      supabase
        .from("metrics_raw")
        .select("*")
        .order("recorded_at", { ascending: false })
        .limit(100),
      supabase
        .from("metrics_aggregated")
        .select("*")
        .order("created_at", { ascending: false })
        .limit(50),
      supabase.from("traces").select("*").order("started_at", { ascending: false }).limit(100),
      supabase.from("anomalies").select("*").order("detected_at", { ascending: false }),
      supabase.from("correlations").select("*").order("calculated_at", { ascending: false }),
    ]);
    if (rawRes.data) setMetricsRaw(rawRes.data);
    if (aggRes.data) setMetricsAggregated(aggRes.data);
    if (tracesRes.data) setTraces(tracesRes.data);
    if (anomaliesRes.data) setAnomalies(anomaliesRes.data);
    if (corrRes.data) setCorrelations(corrRes.data);
    setIsLoading(false);
  };

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const recordMetric = async (metricName: string, value: number, tags?: Record<string, any>) => {
    if (!user) return;
    const { error } = await supabase
      .from("metrics_raw")
      .insert({ user_id: user.id, metric_name: metricName, metric_value: value, tags });
    if (error) toast.error("Failed to record metric");
    else fetchAll();
  };

  const resolveAnomaly = async (id: string) => {
    const { error } = await supabase
      .from("anomalies")
      .update({ is_resolved: true, resolved_at: new Date().toISOString() })
      .eq("id", id);
    if (error) toast.error("Failed to resolve");
    else {
      toast.success("Resolved");
      fetchAll();
    }
  };

  const getAnomalyStats = () => {
    const total = anomalies.length;
    const unresolved = anomalies.filter((a) => !a.is_resolved).length;
    const critical = anomalies.filter((a) => a.severity === "critical").length;
    return { total, unresolved, critical };
  };

  return {
    metricsRaw,
    metricsAggregated,
    traces,
    anomalies,
    correlations,
    isLoading,
    recordMetric,
    resolveAnomaly,
    getAnomalyStats,
  };
}
