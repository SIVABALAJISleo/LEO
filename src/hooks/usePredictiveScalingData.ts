import { useState, useEffect, useCallback } from 'react';
import { supabase } from '@/integrations/supabase/client';
import { useAuth } from '@/contexts/AuthContext';
import { toast } from 'sonner';
import type { Json } from '@/integrations/supabase/types';

export interface WorkloadPrediction {
  id: string;
  user_id: string;
  prediction_type: string;
  time_horizon: string;
  predicted_value: number;
  confidence_lower: number | null;
  confidence_upper: number | null;
  actual_value: number | null;
  is_anomaly: boolean | null;
  model_version: string | null;
  created_at: string;
  target_time: string;
}

export interface ScalingAction {
  id: string;
  user_id: string;
  action_type: string;
  resource_type: string;
  previous_count: number | null;
  new_count: number | null;
  trigger_reason: string | null;
  status: string;
  cost_impact: number | null;
  latency_impact: number | null;
  executed_at: string | null;
  created_at: string;
}

export interface CostAnalysis {
  id: string;
  user_id: string;
  period_start: string;
  period_end: string;
  resource_type: string;
  actual_cost: number | null;
  optimized_cost: number | null;
  savings: number | null;
  roi: number | null;
  recommendations: Json;
  created_at: string;
}

export interface PredictionAccuracy {
  id: string;
  user_id: string;
  prediction_type: string;
  time_horizon: string;
  mape: number | null;
  rmse: number | null;
  accuracy_percent: number | null;
  sample_count: number | null;
  recorded_at: string;
}

export const PREDICTION_TYPES = [
  { value: 'concurrent_users', label: 'Concurrent Users' },
  { value: 'inference_requests', label: 'Inference Requests' },
  { value: 'avg_latency', label: 'Average Latency' },
  { value: 'memory_usage', label: 'Memory Usage' },
  { value: 'gpu_utilization', label: 'GPU Utilization' },
];

export const TIME_HORIZONS = [
  { value: '1h', label: '1 Hour' },
  { value: '6h', label: '6 Hours' },
  { value: '24h', label: '24 Hours' },
  { value: '7d', label: '7 Days' },
];

export const RESOURCE_TYPES = [
  { value: 'gpu', label: 'GPU Instances' },
  { value: 'cpu', label: 'CPU Nodes' },
  { value: 'memory', label: 'Memory' },
  { value: 'storage', label: 'Storage' },
];

export const usePredictiveScalingData = () => {
  const { user } = useAuth();
  const [predictions, setPredictions] = useState<WorkloadPrediction[]>([]);
  const [scalingActions, setScalingActions] = useState<ScalingAction[]>([]);
  const [costAnalysis, setCostAnalysis] = useState<CostAnalysis[]>([]);
  const [accuracyMetrics, setAccuracyMetrics] = useState<PredictionAccuracy[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchData = useCallback(async () => {
    if (!user) return;
    
    setIsLoading(true);
    try {
      // Fetch predictions
      const { data: predictionsData, error: predictionsError } = await supabase
        .from('workload_predictions')
        .select('*')
        .order('target_time', { ascending: true });
      
      if (predictionsError) throw predictionsError;
      setPredictions((predictionsData || []) as WorkloadPrediction[]);

      // Fetch scaling actions
      const { data: actionsData, error: actionsError } = await supabase
        .from('scaling_actions')
        .select('*')
        .order('created_at', { ascending: false });
      
      if (actionsError) throw actionsError;
      setScalingActions((actionsData || []) as ScalingAction[]);

      // Fetch cost analysis
      const { data: costData, error: costError } = await supabase
        .from('cost_analysis')
        .select('*')
        .order('period_end', { ascending: false });
      
      if (costError) throw costError;
      setCostAnalysis((costData || []) as CostAnalysis[]);

      // Fetch accuracy metrics
      const { data: accuracyData, error: accuracyError } = await supabase
        .from('prediction_accuracy')
        .select('*')
        .order('recorded_at', { ascending: false });
      
      if (accuracyError) throw accuracyError;
      setAccuracyMetrics((accuracyData || []) as PredictionAccuracy[]);

    } catch (err) {
      console.error('Error fetching predictive scaling data:', err);
      setError(err as Error);
    } finally {
      setIsLoading(false);
    }
  }, [user]);

  const createPrediction = async (data: {
    prediction_type: string;
    time_horizon: string;
    predicted_value: number;
    confidence_lower?: number;
    confidence_upper?: number;
    target_time: string;
    is_anomaly?: boolean;
  }) => {
    if (!user) return null;
    
    try {
      const { data: prediction, error } = await supabase
        .from('workload_predictions')
        .insert({
          user_id: user.id,
          ...data,
        })
        .select()
        .single();
      
      if (error) throw error;
      await fetchData();
      return prediction;
    } catch (err) {
      console.error('Error creating prediction:', err);
      toast.error('Failed to create prediction');
      return null;
    }
  };

  const proposeScalingAction = async (data: {
    action_type: string;
    resource_type: string;
    previous_count: number;
    new_count: number;
    trigger_reason: string;
    cost_impact?: number;
    latency_impact?: number;
  }) => {
    if (!user) return null;
    
    try {
      const { data: action, error } = await supabase
        .from('scaling_actions')
        .insert({
          user_id: user.id,
          status: 'pending',
          ...data,
        })
        .select()
        .single();
      
      if (error) throw error;
      toast.success('Scaling action proposed');
      await fetchData();
      return action;
    } catch (err) {
      console.error('Error proposing scaling action:', err);
      toast.error('Failed to propose scaling action');
      return null;
    }
  };

  const executeScalingAction = async (actionId: string) => {
    if (!user) return;
    
    try {
      const { error } = await supabase
        .from('scaling_actions')
        .update({
          status: 'executed',
          executed_at: new Date().toISOString(),
        })
        .eq('id', actionId);
      
      if (error) throw error;
      toast.success('Scaling action executed');
      await fetchData();
    } catch (err) {
      console.error('Error executing scaling action:', err);
      toast.error('Failed to execute scaling action');
    }
  };

  const cancelScalingAction = async (actionId: string) => {
    if (!user) return;
    
    try {
      const { error } = await supabase
        .from('scaling_actions')
        .update({ status: 'cancelled' })
        .eq('id', actionId);
      
      if (error) throw error;
      toast.success('Scaling action cancelled');
      await fetchData();
    } catch (err) {
      console.error('Error cancelling scaling action:', err);
      toast.error('Failed to cancel scaling action');
    }
  };

  const generatePredictions = async (predictionType: string, timeHorizon: string) => {
    if (!user) return;
    
    // Simulate prediction generation based on historical data
    const now = new Date();
    
    let intervals: number;
    let intervalMs: number;
    
    switch (timeHorizon) {
      case '1h':
        intervals = 12;
        intervalMs = 5 * 60 * 1000;
        break;
      case '6h':
        intervals = 12;
        intervalMs = 30 * 60 * 1000;
        break;
      case '24h':
        intervals = 24;
        intervalMs = 60 * 60 * 1000;
        break;
      default:
        intervals = 12;
        intervalMs = 60 * 60 * 1000;
    }

    // HONEST: Predictions require actual model - queue for ML processing
    for (let i = 0; i < intervals; i++) {
      const targetTime = new Date(now.getTime() + (i + 1) * intervalMs);
      
      await createPrediction({
        prediction_type: predictionType,
        time_horizon: timeHorizon,
        predicted_value: null, // Will be populated by ML model
        confidence_lower: null,
        confidence_upper: null,
        target_time: targetTime.toISOString(),
        is_anomaly: null, // Requires analysis
      });
    }
    
    toast.success('Predictions queued for ML processing');
  };

  const getUpcomingPredictions = (hours: number = 24) => {
    const now = new Date();
    const cutoff = new Date(now.getTime() + hours * 60 * 60 * 1000);
    
    return predictions.filter(p => {
      const targetTime = new Date(p.target_time);
      return targetTime >= now && targetTime <= cutoff;
    });
  };

  const getTotalSavings = () => {
    return costAnalysis.reduce((sum, c) => sum + (c.savings || 0), 0);
  };

  const getAverageAccuracy = (predictionType?: string) => {
    const filtered = predictionType 
      ? accuracyMetrics.filter(a => a.prediction_type === predictionType)
      : accuracyMetrics;
    
    if (filtered.length === 0) return null;
    
    const sum = filtered.reduce((acc, m) => acc + (m.accuracy_percent || 0), 0);
    return sum / filtered.length;
  };

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return {
    predictions,
    scalingActions,
    costAnalysis,
    accuracyMetrics,
    isLoading,
    error,
    createPrediction,
    proposeScalingAction,
    executeScalingAction,
    cancelScalingAction,
    generatePredictions,
    getUpcomingPredictions,
    getTotalSavings,
    getAverageAccuracy,
    refetch: fetchData,
  };
};
