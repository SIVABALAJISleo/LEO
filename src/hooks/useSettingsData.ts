import { useState, useEffect, useCallback } from 'react';
import { firebaseClient as supabase } from '@/integrations/firebase/client';
import { useAuth } from '@/contexts/AuthContext';
import { useToast } from '@/hooks/use-toast';

export interface Profile {
  id: string;
  user_id: string;
  full_name: string | null;
  company: string | null;
  avatar_url: string | null;
}

export interface ApiKey {
  id: string;
  key_name: string;
  key_prefix: string | null;
  is_active: boolean;
  created_at: string;
  last_used_at: string | null;
  expires_at: string | null;
}

export interface Subscription {
  id: string;
  tier: string;
  status: string;
  api_calls_limit: number;
  api_calls_used: number;
  reset_at: string;
}

export function useSettingsData() {
  const { user } = useAuth();
  const { toast } = useToast();
  const [loading, setLoading] = useState(true);
  const [profile, setProfile] = useState<Profile | null>(null);
  const [apiKeys, setApiKeys] = useState<ApiKey[]>([]);
  const [subscription, setSubscription] = useState<Subscription | null>(null);

  const fetchProfile = useCallback(async () => {
    if (!user) return;

    const { data, error } = await supabase
      .from('profiles')
      .select('*')
      .eq('user_id', user.id)
      .single();

    if (!error && data) {
      setProfile(data);
    }
  }, [user]);

  const fetchApiKeys = useCallback(async () => {
    if (!user) return;

    // Use safe view that excludes key_hash
    const { data, error } = await supabase
      .from('api_keys')
      .select('id, user_id, key_name, key_prefix, is_active, created_at, last_used_at, expires_at')
      .eq('user_id', user.id)
      .order('created_at', { ascending: false });

    if (!error) {
      setApiKeys(data || []);
    }
  }, [user]);

  const fetchSubscription = useCallback(async () => {
    if (!user) return;

    const { data, error } = await supabase
      .from('subscriptions')
      .select('*')
      .eq('user_id', user.id)
      .single();

    if (!error && data) {
      setSubscription(data);
    }
  }, [user]);

  const refreshAll = useCallback(async () => {
    setLoading(true);
    await Promise.all([fetchProfile(), fetchApiKeys(), fetchSubscription()]);
    setLoading(false);
  }, [fetchProfile, fetchApiKeys, fetchSubscription]);

  useEffect(() => {
    refreshAll();
  }, [refreshAll]);

  const updateProfile = async (updates: Partial<Profile>) => {
    if (!user || !profile) return false;

    try {
      const { error } = await supabase
        .from('profiles')
        .update(updates)
        .eq('user_id', user.id);

      if (error) throw error;

      toast({ title: 'Profile Updated', description: 'Your profile has been saved.' });
      await fetchProfile();
      return true;
    } catch (err: any) {
      toast({ title: 'Error', description: err.message, variant: 'destructive' });
      return false;
    }
  };

  const generateApiKey = async (keyName: string) => {
    if (!user) return null;

    try {
      // Use server-side edge function for secure key generation
      const { data, error } = await supabase.functions.invoke('generate-api-key', {
        body: { key_name: keyName }
      });

      if (error) throw error;

      if (!data.success) {
        throw new Error(data.error || 'Failed to generate API key');
      }

      toast({ 
        title: 'API Key Created', 
        description: 'Copy your key now - it won\'t be shown again!' 
      });
      await fetchApiKeys();
      // Return the plaintext key only once for the user to copy
      return data.key;
    } catch (err: any) {
      toast({ title: 'Error', description: err.message, variant: 'destructive' });
      return null;
    }
  };

  const revokeApiKey = async (keyId: string) => {
    if (!user) return;

    try {
      const { error } = await supabase
        .from('api_keys')
        .update({ is_active: false })
        .eq('id', keyId)
        .eq('user_id', user.id);

      if (error) throw error;

      toast({ title: 'API Key Revoked', description: 'The API key has been deactivated.' });
      await fetchApiKeys();
    } catch (err: any) {
      toast({ title: 'Error', description: err.message, variant: 'destructive' });
    }
  };

  const deleteApiKey = async (keyId: string) => {
    if (!user) return;

    try {
      const { error } = await supabase
        .from('api_keys')
        .delete()
        .eq('id', keyId)
        .eq('user_id', user.id);

      if (error) throw error;

      toast({ title: 'API Key Deleted', description: 'The API key has been permanently deleted.' });
      await fetchApiKeys();
    } catch (err: any) {
      toast({ title: 'Error', description: err.message, variant: 'destructive' });
    }
  };

  return {
    loading,
    profile,
    apiKeys,
    subscription,
    updateProfile,
    generateApiKey,
    revokeApiKey,
    deleteApiKey,
    refreshAll
  };
}
