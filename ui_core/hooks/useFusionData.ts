import { useState, useEffect } from "react";
import { firebaseClient as supabase } from "@/integrations/firebase/client";
import { useAuth } from "@/contexts/AuthContext";
import { toast } from "sonner";

export const FUSION_STRATEGIES = [
  { value: "early", label: "Early Fusion", desc: "Combine inputs before processing" },
  { value: "late", label: "Late Fusion", desc: "Combine outputs after processing" },
  { value: "intermediate", label: "Intermediate Fusion", desc: "Merge at hidden layers" },
  { value: "ensemble", label: "Ensemble", desc: "Weighted voting of multiple models" },
];

export const CONFLICT_RESOLUTIONS = [
  { value: "weighted_average", label: "Weighted Average" },
  { value: "max_confidence", label: "Max Confidence" },
  { value: "voting", label: "Majority Voting" },
  { value: "learned", label: "Learned Attention" },
];

export function useFusionData() {
  const { user } = useAuth();
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [fusedModels, setFusedModels] = useState<any[]>([]);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [strategies, setStrategies] = useState<any[]>([]);
  // eslint-disable-next-line @typescript-eslint/no-unused-vars, @typescript-eslint/no-explicit-any
  const [performanceLogs, setPerformanceLogs] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (user) fetchAll();
  }, [user]);

  const fetchAll = async () => {
    setIsLoading(true);
    const [modelsRes, strategiesRes] = await Promise.all([
      supabase.from("fused_models").select("*").order("created_at", { ascending: false }),
      supabase.from("fusion_strategies").select("*").order("created_at", { ascending: false }),
    ]);
    if (modelsRes.data) setFusedModels(modelsRes.data);
    if (strategiesRes.data) setStrategies(strategiesRes.data);
    setIsLoading(false);
  };

  const createFusedModel = async (data: {
    name: string;
    fusion_strategy: string;
    description?: string;
  }) => {
    if (!user) return;
    const { error } = await supabase.from("fused_models").insert({ ...data, user_id: user.id });
    if (error) toast.error("Failed to create model");
    else {
      toast.success("Fused model created");
      fetchAll();
    }
  };

  const createStrategy = async (data: {
    name: string;
    strategy_type: string;
    conflict_resolution?: string;
  }) => {
    if (!user) return;
    const { error } = await supabase
      .from("fusion_strategies")
      .insert({ ...data, user_id: user.id });
    if (error) toast.error("Failed to create strategy");
    else {
      toast.success("Strategy created");
      fetchAll();
    }
  };

  const deleteFusedModel = async (id: string) => {
    const { error } = await supabase.from("fused_models").delete().eq("id", id);
    if (error) toast.error("Failed to delete");
    else {
      toast.success("Deleted");
      fetchAll();
    }
  };

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const updateFusedModel = async (id: string, data: Partial<any>) => {
    const { error } = await supabase.from("fused_models").update(data).eq("id", id);
    if (error) toast.error("Failed to update");
    else {
      toast.success("Updated");
      fetchAll();
    }
  };

  return {
    fusedModels,
    strategies,
    performanceLogs,
    isLoading,
    createFusedModel,
    createStrategy,
    deleteFusedModel,
    updateFusedModel,
  };
}
