import { useState, useEffect, useCallback } from 'react';
import { supabase } from '@/integrations/supabase/client';
import { useAuth } from '@/contexts/AuthContext';
import { toast } from 'sonner';
import type { Json } from '@/integrations/supabase/types';

export interface CloudProvider {
  id: string;
  user_id: string;
  provider_name: string;
  region: string;
  is_active: boolean | null;
  credentials_configured: boolean | null;
  capabilities: Json;
  priority: number | null;
  created_at: string;
  updated_at: string;
}

export interface CloudCost {
  id: string;
  provider_id: string | null;
  resource_type: string;
  cost_per_hour: number | null;
  cost_per_request: number | null;
  recorded_at: string;
}

export interface CloudLatency {
  id: string;
  provider_id: string | null;
  endpoint_type: string;
  latency_ms: number;
  success: boolean | null;
  recorded_at: string;
}

export interface CloudFailoverLog {
  id: string;
  user_id: string;
  from_provider_id: string | null;
  to_provider_id: string | null;
  reason: string;
  duration_ms: number | null;
  success: boolean | null;
  created_at: string;
}

export interface CloudRoutingRule {
  id: string;
  user_id: string;
  name: string;
  mode: string;
  conditions: Json;
  is_active: boolean | null;
  created_at: string;
}

export const CLOUD_PROVIDERS_LIST = [
  { value: 'aws', label: 'Amazon Web Services', icon: '🟠' },
  { value: 'gcp', label: 'Google Cloud Platform', icon: '🔵' },
  { value: 'azure', label: 'Microsoft Azure', icon: '🔷' },
];

export const ROUTING_MODES = [
  { value: 'lowest_latency', label: 'Lowest Latency', description: 'Route to fastest responding provider' },
  { value: 'lowest_cost', label: 'Lowest Cost', description: 'Route to cheapest provider' },
  { value: 'balanced', label: 'Balanced', description: 'Balance between cost and latency' },
  { value: 'round_robin', label: 'Round Robin', description: 'Distribute evenly across providers' },
];

export const REGIONS = {
  aws: ['us-east-1', 'us-west-2', 'eu-west-1', 'ap-northeast-1', 'ap-southeast-1'],
  gcp: ['us-central1', 'us-east1', 'europe-west1', 'asia-east1', 'asia-southeast1'],
  azure: ['eastus', 'westus2', 'westeurope', 'japaneast', 'southeastasia'],
};

export const useMultiCloudData = () => {
  const { user } = useAuth();
  const [providers, setProviders] = useState<CloudProvider[]>([]);
  const [costs, setCosts] = useState<CloudCost[]>([]);
  const [latencies, setLatencies] = useState<CloudLatency[]>([]);
  const [failoverLogs, setFailoverLogs] = useState<CloudFailoverLog[]>([]);
  const [routingRules, setRoutingRules] = useState<CloudRoutingRule[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchData = useCallback(async () => {
    if (!user) return;
    
    setIsLoading(true);
    try {
      // Fetch providers
      const { data: providersData, error: providersError } = await supabase
        .from('cloud_providers')
        .select('*')
        .order('priority', { ascending: true });
      
      if (providersError) throw providersError;
      setProviders((providersData || []) as CloudProvider[]);

      // Fetch costs
      const providerIds = (providersData || []).map(p => p.id);
      if (providerIds.length > 0) {
        const { data: costsData } = await supabase
          .from('cloud_costs')
          .select('*')
          .in('provider_id', providerIds)
          .order('recorded_at', { ascending: false });
        setCosts((costsData || []) as CloudCost[]);

        // Fetch latencies
        const { data: latenciesData } = await supabase
          .from('cloud_latencies')
          .select('*')
          .in('provider_id', providerIds)
          .order('recorded_at', { ascending: false });
        setLatencies((latenciesData || []) as CloudLatency[]);
      }

      // Fetch failover logs
      const { data: failoverData, error: failoverError } = await supabase
        .from('cloud_failover_log')
        .select('*')
        .order('created_at', { ascending: false })
        .limit(100);
      
      if (failoverError) throw failoverError;
      setFailoverLogs((failoverData || []) as CloudFailoverLog[]);

      // Fetch routing rules
      const { data: rulesData, error: rulesError } = await supabase
        .from('cloud_routing_rules')
        .select('*')
        .order('created_at', { ascending: false });
      
      if (rulesError) throw rulesError;
      setRoutingRules((rulesData || []) as CloudRoutingRule[]);

    } catch (err) {
      console.error('Error fetching multi-cloud data:', err);
      setError(err as Error);
    } finally {
      setIsLoading(false);
    }
  }, [user]);

  const addProvider = async (data: {
    provider_name: string;
    region: string;
    priority?: number;
    capabilities?: Json;
  }) => {
    if (!user) return null;
    
    try {
      const { data: provider, error } = await supabase
        .from('cloud_providers')
        .insert({
          user_id: user.id,
          provider_name: data.provider_name,
          region: data.region,
          priority: data.priority || 5,
          capabilities: data.capabilities || {},
        })
        .select()
        .single();
      
      if (error) throw error;
      toast.success('Cloud provider added');
      await fetchData();
      return provider;
    } catch (err) {
      console.error('Error adding provider:', err);
      toast.error('Failed to add provider');
      return null;
    }
  };

  const updateProvider = async (providerId: string, updates: {
    is_active?: boolean;
    priority?: number;
    credentials_configured?: boolean;
  }) => {
    if (!user) return;
    
    try {
      const { error } = await supabase
        .from('cloud_providers')
        .update({ ...updates, updated_at: new Date().toISOString() })
        .eq('id', providerId);
      
      if (error) throw error;
      toast.success('Provider updated');
      await fetchData();
    } catch (err) {
      console.error('Error updating provider:', err);
      toast.error('Failed to update provider');
    }
  };

  const deleteProvider = async (providerId: string) => {
    if (!user) return;
    
    try {
      const { error } = await supabase
        .from('cloud_providers')
        .delete()
        .eq('id', providerId);
      
      if (error) throw error;
      toast.success('Provider deleted');
      await fetchData();
    } catch (err) {
      console.error('Error deleting provider:', err);
      toast.error('Failed to delete provider');
    }
  };

  const createRoutingRule = async (data: {
    name: string;
    mode: string;
    conditions?: Json;
  }) => {
    if (!user) return null;
    
    try {
      const { data: rule, error } = await supabase
        .from('cloud_routing_rules')
        .insert({
          user_id: user.id,
          name: data.name,
          mode: data.mode,
          conditions: data.conditions || {},
        })
        .select()
        .single();
      
      if (error) throw error;
      toast.success('Routing rule created');
      await fetchData();
      return rule;
    } catch (err) {
      console.error('Error creating routing rule:', err);
      toast.error('Failed to create routing rule');
      return null;
    }
  };

  const toggleRoutingRule = async (ruleId: string, isActive: boolean) => {
    if (!user) return;
    
    try {
      const { error } = await supabase
        .from('cloud_routing_rules')
        .update({ is_active: isActive })
        .eq('id', ruleId);
      
      if (error) throw error;
      toast.success(isActive ? 'Rule activated' : 'Rule deactivated');
      await fetchData();
    } catch (err) {
      console.error('Error toggling routing rule:', err);
      toast.error('Failed to toggle rule');
    }
  };

  const getProviderStats = (providerId: string) => {
    const providerCosts = costs.filter(c => c.provider_id === providerId);
    const providerLatencies = latencies.filter(l => l.provider_id === providerId);
    
    const avgLatency = providerLatencies.length > 0
      ? providerLatencies.reduce((sum, l) => sum + l.latency_ms, 0) / providerLatencies.length
      : null;
    
    const successRate = providerLatencies.length > 0
      ? (providerLatencies.filter(l => l.success).length / providerLatencies.length) * 100
      : null;
    
    const latestCost = providerCosts[0] || null;
    
    return { avgLatency, successRate, latestCost };
  };

  const getBestProvider = (mode: string = 'balanced') => {
    if (providers.length === 0) return null;
    
    const activeProviders = providers.filter(p => p.is_active);
    if (activeProviders.length === 0) return null;
    
    switch (mode) {
      case 'lowest_latency':
        return activeProviders.reduce((best, current) => {
          const bestStats = getProviderStats(best.id);
          const currentStats = getProviderStats(current.id);
          if (!currentStats.avgLatency) return best;
          if (!bestStats.avgLatency) return current;
          return currentStats.avgLatency < bestStats.avgLatency ? current : best;
        });
      
      case 'lowest_cost':
        return activeProviders.reduce((best, current) => {
          const bestStats = getProviderStats(best.id);
          const currentStats = getProviderStats(current.id);
          if (!currentStats.latestCost?.cost_per_request) return best;
          if (!bestStats.latestCost?.cost_per_request) return current;
          return currentStats.latestCost.cost_per_request < bestStats.latestCost.cost_per_request ? current : best;
        });
      
      default:
        return activeProviders.sort((a, b) => (a.priority || 5) - (b.priority || 5))[0];
    }
  };

  const simulateFailover = async (fromProviderId: string, reason: string) => {
    if (!user) return;
    
    const activeProviders = providers.filter(p => p.is_active && p.id !== fromProviderId);
    if (activeProviders.length === 0) {
      toast.error('No backup providers available');
      return;
    }
    
    const toProvider = getBestProvider('lowest_latency');
    if (!toProvider) return;
    
    toast.success(`Failover simulated: ${reason}`);
  };

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return {
    providers,
    costs,
    latencies,
    failoverLogs,
    routingRules,
    isLoading,
    error,
    addProvider,
    updateProvider,
    deleteProvider,
    createRoutingRule,
    toggleRoutingRule,
    getProviderStats,
    getBestProvider,
    simulateFailover,
    refetch: fetchData,
  };
};
