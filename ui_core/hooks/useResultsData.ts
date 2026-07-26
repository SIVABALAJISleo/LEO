import { useState, useEffect, useCallback } from "react";
import { firebaseClient as supabase } from "@/integrations/firebase/client";
import { useAuth } from "@/contexts/AuthContext";
import { InferenceJob } from "./useJobsData";

export function useResultsData() {
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [completedJobs, setCompletedJobs] = useState<InferenceJob[]>([]);
  const [selectedJobs, setSelectedJobs] = useState<string[]>([]);

  const fetchCompletedJobs = useCallback(async () => {
    if (!user) return;

    try {
      setLoading(true);
      const { data, error: fetchError } = await supabase
        .from("inference_jobs")
        .select(
          `
          *,
          model:models(id, name, model_type)
        `,
        )
        .eq("user_id", user.id)
        .in("status", ["completed", "failed"])
        .order("completed_at", { ascending: false })
        .limit(100);

      if (fetchError) throw fetchError;
      setCompletedJobs(data || []);
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [user]);

  useEffect(() => {
    fetchCompletedJobs();
  }, [fetchCompletedJobs]);

  const toggleJobSelection = (jobId: string) => {
    setSelectedJobs((prev) =>
      prev.includes(jobId) ? prev.filter((id) => id !== jobId) : [...prev, jobId],
    );
  };

  const clearSelection = () => {
    setSelectedJobs([]);
  };

  const getSelectedJobsData = () => {
    return completedJobs.filter((job) => selectedJobs.includes(job.id));
  };

  const exportToJson = (jobs: InferenceJob[]) => {
    const data = JSON.stringify(jobs, null, 2);
    const blob = new Blob([data], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `inference-results-${new Date().toISOString().split("T")[0]}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const exportToCsv = (jobs: InferenceJob[]) => {
    const headers = [
      "ID",
      "Model",
      "Status",
      "Latency (ms)",
      "Speedup",
      "Compression",
      "Created",
      "Completed",
    ];
    const rows = jobs.map((job) => [
      job.id,
      job.model?.name || job.model_id,
      job.status,
      job.latency_ms || "",
      job.speedup || "",
      job.compression_ratio || "",
      job.created_at,
      job.completed_at || "",
    ]);

    const csv = [headers, ...rows].map((row) => row.join(",")).join("\n");
    const blob = new Blob([csv], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `inference-results-${new Date().toISOString().split("T")[0]}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return {
    loading,
    error,
    completedJobs,
    selectedJobs,
    toggleJobSelection,
    clearSelection,
    getSelectedJobsData,
    exportToJson,
    exportToCsv,
    refetch: fetchCompletedJobs,
  };
}
