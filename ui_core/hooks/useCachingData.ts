import { useState, useEffect, useCallback } from "react";
import { firebaseClient as supabase } from "@/integrations/firebase/client";
import { useAuth } from "@/contexts/AuthContext";
import { toast } from "sonner";

export interface CacheMetadata {
  id: string;
  user_id: string;
  cache_key: string;
  cache_level: string;
  content_type: string | null;
  size_bytes: number | null;
  hit_count: number;
  last_accessed_at: string | null;
  expires_at: string | null;
  created_at: string;
}

export interface CacheAnalytics {
  id: string;
  user_id: string;
  cache_level: string;
  hits: number;
  misses: number;
  evictions: number;
  avg_response_time_saved_ms: number | null;
  total_size_bytes: number;
  recorded_at: string;
}

export interface CacheInvalidationLog {
  id: string;
  user_id: string;
  cache_level: string;
  invalidation_type: string;
  affected_keys: number | null;
  reason: string | null;
  created_at: string;
}

export interface SemanticEmbedding {
  id: string;
  user_id: string;
  query_hash: string;
  embedding: number[] | null;
  cache_key: string | null;
  similarity_threshold: number;
  hit_count: number;
  created_at: string;
}

export interface CacheWarmingJob {
  id: string;
  user_id: string;
  job_type: string;
  status: string;
  target_cache_level: string | null;
  items_to_warm: number | null;
  items_warmed: number;
  trigger_reason: string | null;
  started_at: string | null;
  completed_at: string | null;
  created_at: string;
}

export const CACHE_LEVELS = [
  { value: "L1", label: "L1 - Local Device", size: "500MB", ttl: "24h", policy: "LRU" },
  { value: "L2", label: "L2 - Edge (Redis)", size: "10GB", ttl: "7d", policy: "LFU" },
  { value: "L3", label: "L3 - Cloud Storage", size: "100GB", ttl: "30d", policy: "TTL" },
];

export const INVALIDATION_TYPES = [
  { value: "ttl", label: "TTL Expiry", description: "Automatic expiration based on time-to-live" },
  { value: "model_update", label: "Model Update", description: "Invalidate when model is updated" },
  { value: "manual", label: "Manual Clear", description: "Manually triggered cache clear" },
  {
    value: "lru_eviction",
    label: "LRU Eviction",
    description: "Evicted due to cache full (least recently used)",
  },
];

export const useCachingData = () => {
  const { user } = useAuth();
  const [cacheMetadata, setCacheMetadata] = useState<CacheMetadata[]>([]);
  const [analytics, setAnalytics] = useState<CacheAnalytics[]>([]);
  const [invalidationLogs, setInvalidationLogs] = useState<CacheInvalidationLog[]>([]);
  const [semanticEmbeddings, setSemanticEmbeddings] = useState<SemanticEmbedding[]>([]);
  const [warmingJobs, setWarmingJobs] = useState<CacheWarmingJob[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchData = useCallback(async () => {
    if (!user) return;

    setIsLoading(true);
    try {
      // Fetch cache metadata
      const { data: metadataData, error: metadataError } = await supabase
        .from("cache_metadata")
        .select("*")
        .order("hit_count", { ascending: false });

      if (metadataError) throw metadataError;
      setCacheMetadata(metadataData || []);

      // Fetch analytics
      const { data: analyticsData, error: analyticsError } = await supabase
        .from("cache_analytics")
        .select("*")
        .order("recorded_at", { ascending: false });

      if (analyticsError) throw analyticsError;
      setAnalytics(analyticsData || []);

      // Fetch invalidation logs
      const { data: logsData, error: logsError } = await supabase
        .from("cache_invalidation_log")
        .select("*")
        .order("created_at", { ascending: false })
        .limit(100);

      if (logsError) throw logsError;
      setInvalidationLogs(logsData || []);

      // Fetch semantic embeddings
      const { data: embeddingsData, error: embeddingsError } = await supabase
        .from("semantic_embeddings")
        .select("*")
        .order("hit_count", { ascending: false });

      if (embeddingsError) throw embeddingsError;
      setSemanticEmbeddings(embeddingsData || []);

      // Fetch warming jobs
      const { data: warmingData, error: warmingError } = await supabase
        .from("cache_warming_jobs")
        .select("*")
        .order("created_at", { ascending: false });

      if (warmingError) throw warmingError;
      setWarmingJobs(warmingData || []);
    } catch (err) {
      console.error("Error fetching caching data:", err);
      setError(err as Error);
    } finally {
      setIsLoading(false);
    }
  }, [user]);

  const addCacheEntry = async (data: {
    cache_key: string;
    cache_level: string;
    content_type?: string;
    size_bytes?: number;
    expires_at?: string;
  }) => {
    if (!user) return null;

    try {
      const { data: entry, error } = await supabase
        .from("cache_metadata")
        .insert({
          user_id: user.id,
          cache_key: data.cache_key,
          cache_level: data.cache_level,
          content_type: data.content_type,
          size_bytes: data.size_bytes,
          expires_at: data.expires_at,
        })
        .select()
        .single();

      if (error) throw error;
      await fetchData();
      return entry;
    } catch (err) {
      console.error("Error adding cache entry:", err);
      toast.error("Failed to add cache entry");
      return null;
    }
  };

  const invalidateCache = async (cacheLevel: string, invalidationType: string, reason?: string) => {
    if (!user) return;

    try {
      const affectedEntries = cacheMetadata.filter((c) => c.cache_level === cacheLevel);

      // Delete entries
      const { error: deleteError } = await supabase
        .from("cache_metadata")
        .delete()
        .eq("cache_level", cacheLevel);

      if (deleteError) throw deleteError;

      // Log invalidation
      const { error: logError } = await supabase.from("cache_invalidation_log").insert({
        user_id: user.id,
        cache_level: cacheLevel,
        invalidation_type: invalidationType,
        affected_keys: affectedEntries.length,
        reason,
      });

      if (logError) throw logError;

      toast.success(`Invalidated ${affectedEntries.length} cache entries`);
      await fetchData();
    } catch (err) {
      console.error("Error invalidating cache:", err);
      toast.error("Failed to invalidate cache");
    }
  };

  const deleteCacheEntry = async (entryId: string) => {
    if (!user) return;

    try {
      const { error } = await supabase.from("cache_metadata").delete().eq("id", entryId);

      if (error) throw error;
      toast.success("Cache entry deleted");
      await fetchData();
    } catch (err) {
      console.error("Error deleting cache entry:", err);
      toast.error("Failed to delete cache entry");
    }
  };

  const startWarmingJob = async (data: {
    job_type: string;
    target_cache_level: string;
    items_to_warm: number;
    trigger_reason?: string;
  }) => {
    if (!user) return null;

    try {
      const { data: job, error } = await supabase
        .from("cache_warming_jobs")
        .insert({
          user_id: user.id,
          job_type: data.job_type,
          target_cache_level: data.target_cache_level,
          items_to_warm: data.items_to_warm,
          trigger_reason: data.trigger_reason,
          status: "pending",
        })
        .select()
        .single();

      if (error) throw error;
      toast.success("Cache warming job started");
      await fetchData();
      return job;
    } catch (err) {
      console.error("Error starting warming job:", err);
      toast.error("Failed to start warming job");
      return null;
    }
  };

  const updateWarmingJobProgress = async (jobId: string, itemsWarmed: number, status?: string) => {
    if (!user) return;

    try {
      const updates: Record<string, unknown> = { items_warmed: itemsWarmed };
      if (status) {
        updates.status = status;
        if (status === "running" && !warmingJobs.find((j) => j.id === jobId)?.started_at) {
          updates.started_at = new Date().toISOString();
        }
        if (status === "completed" || status === "failed") {
          updates.completed_at = new Date().toISOString();
        }
      }

      const { error } = await supabase.from("cache_warming_jobs").update(updates).eq("id", jobId);

      if (error) throw error;
      await fetchData();
    } catch (err) {
      console.error("Error updating warming job:", err);
    }
  };

  const recordAnalytics = async (
    cacheLevel: string,
    hits: number,
    misses: number,
    evictions: number = 0,
  ) => {
    if (!user) return;

    try {
      const levelMetadata = cacheMetadata.filter((c) => c.cache_level === cacheLevel);
      const totalSize = levelMetadata.reduce((sum, c) => sum + (c.size_bytes || 0), 0);

      const { error } = await supabase.from("cache_analytics").insert({
        user_id: user.id,
        cache_level: cacheLevel,
        hits,
        misses,
        evictions,
        total_size_bytes: totalSize,
        avg_response_time_saved_ms: null, // HONEST: Requires real measurement
      });

      if (error) throw error;
    } catch (err) {
      console.error("Error recording analytics:", err);
    }
  };

  const getHitRateByLevel = (level: string) => {
    const levelAnalytics = analytics.filter((a) => a.cache_level === level);
    if (levelAnalytics.length === 0) return 0;

    const totalHits = levelAnalytics.reduce((sum, a) => sum + a.hits, 0);
    const totalMisses = levelAnalytics.reduce((sum, a) => sum + a.misses, 0);
    const total = totalHits + totalMisses;

    return total > 0 ? (totalHits / total) * 100 : 0;
  };

  const getTotalSizeByLevel = (level: string) => {
    return cacheMetadata
      .filter((c) => c.cache_level === level)
      .reduce((sum, c) => sum + (c.size_bytes || 0), 0);
  };

  const getTopCachedQueries = (limit: number = 10) => {
    return [...cacheMetadata].sort((a, b) => b.hit_count - a.hit_count).slice(0, limit);
  };

  const getEstimatedSpeedup = () => {
    const recentAnalytics = analytics.slice(0, 24); // Last 24 records
    if (recentAnalytics.length === 0) return 0;

    const avgTimeSaved =
      recentAnalytics.reduce((sum, a) => sum + (a.avg_response_time_saved_ms || 0), 0) /
      recentAnalytics.length;
    const totalHits = recentAnalytics.reduce((sum, a) => sum + a.hits, 0);

    return (avgTimeSaved * totalHits) / 1000; // Total seconds saved
  };

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return {
    cacheMetadata,
    analytics,
    invalidationLogs,
    semanticEmbeddings,
    warmingJobs,
    isLoading,
    error,
    addCacheEntry,
    invalidateCache,
    deleteCacheEntry,
    startWarmingJob,
    updateWarmingJobProgress,
    recordAnalytics,
    getHitRateByLevel,
    getTotalSizeByLevel,
    getTopCachedQueries,
    getEstimatedSpeedup,
    refetch: fetchData,
  };
};
