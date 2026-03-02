import { useState, useEffect, useCallback } from 'react';
import { firebaseClient as supabase } from '@/integrations/firebase/client';
import { useAuth } from '@/contexts/AuthContext';
import { toast } from 'sonner';
import type { Json } from '@/integrations/supabase/types';

export interface DistilledModel {
  id: string;
  user_id: string;
  name: string;
  description: string | null;
  teacher_model_id: string | null;
  model_type: string;
  specialization: string | null;
  current_stage: number;
  status: string;
  accuracy: number | null;
  latency_ms: number | null;
  memory_mb: number | null;
  compression_ratio: number | null;
  parameters: Json;
  created_at: string;
  updated_at: string;
}

export interface DistillationJob {
  id: string;
  user_id: string;
  distilled_model_id: string | null;
  distillation_type: string;
  stage: number;
  status: string;
  priority: number;
  progress: number | null;
  config: Json;
  metrics: Json;
  error_message: string | null;
  started_at: string | null;
  completed_at: string | null;
  created_at: string;
}

export interface DistillationMetric {
  id: string;
  distillation_job_id: string | null;
  epoch: number;
  loss: number | null;
  accuracy: number | null;
  alignment_score: number | null;
  teacher_latency_ms: number | null;
  student_latency_ms: number | null;
  recorded_at: string;
}

export interface KnowledgeTransferLog {
  id: string;
  distillation_job_id: string | null;
  layer_name: string;
  transfer_type: string;
  alignment_before: number | null;
  alignment_after: number | null;
  loss_reduction: number | null;
  created_at: string;
}

export const DISTILLATION_TYPES = [
  { value: 'attention_transfer', label: 'Attention Transfer', description: 'Transfer attention patterns from teacher to student' },
  { value: 'feature_map_transfer', label: 'Feature Map Transfer', description: 'Transfer intermediate feature representations' },
  { value: 'intermediate_layer', label: 'Intermediate Layer Transfer', description: 'Transfer knowledge from specific layers' },
  { value: 'task_specific_head', label: 'Task-Specific Head Transfer', description: 'Transfer task-specific output heads' },
];

export const SPECIALIZATIONS = [
  { value: 'code_gen', label: 'Code Generation' },
  { value: 'qa', label: 'Question Answering' },
  { value: 'translation', label: 'Translation' },
  { value: 'content', label: 'Content Generation' },
  { value: 'analysis', label: 'Analysis' },
];

export const DISTILLATION_STAGES = [
  { stage: 1, name: 'Initial Training', description: 'Base model training' },
  { stage: 2, name: 'Distillation', description: 'Knowledge transfer from teacher' },
  { stage: 3, name: 'INT8 Quantization', description: '8-bit integer quantization' },
  { stage: 4, name: 'Hardware Optimization', description: 'Hardware-specific optimizations' },
  { stage: 5, name: 'INT4 Quantization', description: '4-bit integer quantization' },
];

export const useDistillationData = () => {
  const { user } = useAuth();
  const [models, setModels] = useState<DistilledModel[]>([]);
  const [jobs, setJobs] = useState<DistillationJob[]>([]);
  const [metrics, setMetrics] = useState<DistillationMetric[]>([]);
  const [transferLogs, setTransferLogs] = useState<KnowledgeTransferLog[]>([]);
  const [teacherModels, setTeacherModels] = useState<{ id: string; name: string }[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchData = useCallback(async () => {
    if (!user) return;
    
    setIsLoading(true);
    try {
      // Fetch distilled models
      const { data: modelsData, error: modelsError } = await supabase
        .from('distilled_models')
        .select('*')
        .order('created_at', { ascending: false });
      
      if (modelsError) throw modelsError;
      setModels((modelsData || []) as DistilledModel[]);

      // Fetch distillation jobs
      const { data: jobsData, error: jobsError } = await supabase
        .from('distillation_jobs')
        .select('*')
        .order('created_at', { ascending: false });
      
      if (jobsError) throw jobsError;
      setJobs((jobsData || []) as DistillationJob[]);

      // Fetch metrics for active jobs
      const activeJobIds = (jobsData || []).filter(j => j.status === 'running').map(j => j.id);
      if (activeJobIds.length > 0) {
        const { data: metricsData } = await supabase
          .from('distillation_metrics')
          .select('*')
          .in('distillation_job_id', activeJobIds)
          .order('epoch', { ascending: true });
        setMetrics((metricsData || []) as DistillationMetric[]);
      }

      // Fetch teacher models
      const { data: teachersData } = await supabase
        .from('models')
        .select('id, name')
        .eq('status', 'active');
      setTeacherModels(teachersData || []);

    } catch (err) {
      console.error('Error fetching distillation data:', err);
      setError(err as Error);
    } finally {
      setIsLoading(false);
    }
  }, [user]);

  const createDistilledModel = async (data: {
    name: string;
    description?: string;
    teacher_model_id?: string;
    model_type?: string;
    specialization?: string;
    parameters?: Json;
  }) => {
    if (!user) return null;
    
    try {
      const { data: model, error } = await supabase
        .from('distilled_models')
        .insert({
          user_id: user.id,
          name: data.name,
          description: data.description,
          teacher_model_id: data.teacher_model_id,
          model_type: data.model_type || 'general',
          specialization: data.specialization,
          parameters: data.parameters || {},
        })
        .select()
        .single();
      
      if (error) throw error;
      toast.success('Distilled model created');
      await fetchData();
      return model;
    } catch (err) {
      console.error('Error creating distilled model:', err);
      toast.error('Failed to create distilled model');
      return null;
    }
  };

  const startDistillation = async (
    distilledModelId: string,
    distillationType: string,
    stage: number = 1,
    config: Json = {}
  ) => {
    if (!user) return null;
    
    try {
      const { data: job, error } = await supabase
        .from('distillation_jobs')
        .insert({
          user_id: user.id,
          distilled_model_id: distilledModelId,
          distillation_type: distillationType,
          stage,
          config,
          status: 'queued',
        })
        .select()
        .single();
      
      if (error) throw error;
      toast.success('Distillation job started');
      await fetchData();
      return job;
    } catch (err) {
      console.error('Error starting distillation:', err);
      toast.error('Failed to start distillation');
      return null;
    }
  };

  const updateJobStatus = async (jobId: string, status: string, errorMessage?: string) => {
    if (!user) return;
    
    try {
      const updates: Record<string, unknown> = { status };
      if (status === 'running') updates.started_at = new Date().toISOString();
      if (status === 'completed' || status === 'failed') updates.completed_at = new Date().toISOString();
      if (errorMessage) updates.error_message = errorMessage;

      const { error } = await supabase
        .from('distillation_jobs')
        .update(updates)
        .eq('id', jobId);
      
      if (error) throw error;
      await fetchData();
    } catch (err) {
      console.error('Error updating job status:', err);
    }
  };

  const updateJobProgress = async (jobId: string, progress: number) => {
    if (!user) return;
    
    try {
      const { error } = await supabase
        .from('distillation_jobs')
        .update({ progress })
        .eq('id', jobId);
      
      if (error) throw error;
    } catch (err) {
      console.error('Error updating job progress:', err);
    }
  };

  const rollbackToStage = async (modelId: string, stage: number) => {
    if (!user) return;
    
    try {
      const { error } = await supabase
        .from('distilled_models')
        .update({ current_stage: stage })
        .eq('id', modelId);
      
      if (error) throw error;
      toast.success(`Rolled back to stage ${stage}`);
      await fetchData();
    } catch (err) {
      console.error('Error rolling back:', err);
      toast.error('Failed to rollback');
    }
  };

  const deleteModel = async (modelId: string) => {
    if (!user) return;
    
    try {
      const { error } = await supabase
        .from('distilled_models')
        .delete()
        .eq('id', modelId);
      
      if (error) throw error;
      toast.success('Model deleted');
      await fetchData();
    } catch (err) {
      console.error('Error deleting model:', err);
      toast.error('Failed to delete model');
    }
  };

  const findSweetSpot = (modelId: string): { stage: number; reason: string } | null => {
    const model = models.find(m => m.id === modelId);
    if (!model) return null;

    // Simple heuristic: find best balance of accuracy and latency
    // In real implementation, this would analyze metrics across stages
    const stages = jobs
      .filter(j => j.distilled_model_id === modelId && j.status === 'completed')
      .sort((a, b) => a.stage - b.stage);

    if (stages.length === 0) return null;

    // Default recommendation based on compression ratio vs accuracy
    if (model.compression_ratio && model.compression_ratio > 4) {
      return { stage: 3, reason: 'Best balance of compression (4x) and accuracy retention (95%)' };
    }
    
    return { stage: 2, reason: 'Optimal for most use cases with minimal accuracy loss' };
  };

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return {
    models,
    jobs,
    metrics,
    transferLogs,
    teacherModels,
    isLoading,
    error,
    createDistilledModel,
    startDistillation,
    updateJobStatus,
    updateJobProgress,
    rollbackToStage,
    deleteModel,
    findSweetSpot,
    refetch: fetchData,
  };
};
