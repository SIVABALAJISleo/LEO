import { useState, useEffect } from 'react';
import { supabase } from '@/integrations/supabase/client';
import { useAuth } from '@/contexts/AuthContext';
import { toast } from 'sonner';

export const PLUGIN_CATEGORIES = [
  { value: 'analytics', label: 'Analytics' },
  { value: 'integration', label: 'Integration' },
  { value: 'optimization', label: 'Optimization' },
  { value: 'security', label: 'Security' },
  { value: 'visualization', label: 'Visualization' },
];

export function useMarketplaceData() {
  const { user } = useAuth();
  const [plugins, setPlugins] = useState<any[]>([]);
  const [myPlugins, setMyPlugins] = useState<any[]>([]);
  const [integrations, setIntegrations] = useState<any[]>([]);
  const [transactions, setTransactions] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (user) fetchAll();
  }, [user]);

  const fetchAll = async () => {
    setIsLoading(true);
    const [allPluginsRes, myPluginsRes, integrationsRes, txRes] = await Promise.all([
      supabase.from('plugins').select('*').eq('is_published', true).order('download_count', { ascending: false }),
      supabase.from('plugins').select('*').eq('author_id', user?.id || ''),
      supabase.from('integrations').select('*, plugins(name, icon_url)').order('created_at', { ascending: false }),
      supabase.from('marketplace_transactions').select('*').order('created_at', { ascending: false }),
    ]);
    if (allPluginsRes.data) setPlugins(allPluginsRes.data);
    if (myPluginsRes.data) setMyPlugins(myPluginsRes.data);
    if (integrationsRes.data) setIntegrations(integrationsRes.data);
    if (txRes.data) setTransactions(txRes.data);
    setIsLoading(false);
  };

  const createPlugin = async (data: { name: string; description?: string; category?: string; version?: string }) => {
    if (!user) return;
    const { error } = await supabase.from('plugins').insert({ ...data, author_id: user.id });
    if (error) toast.error('Failed to create plugin');
    else { toast.success('Plugin created'); fetchAll(); }
  };

  const publishPlugin = async (id: string) => {
    const { error } = await supabase.from('plugins').update({ is_published: true }).eq('id', id);
    if (error) toast.error('Failed to publish');
    else { toast.success('Plugin published'); fetchAll(); }
  };

  const installPlugin = async (pluginId: string) => {
    if (!user) return;
    const plugin = plugins.find(p => p.id === pluginId);
    const { error } = await supabase.from('integrations').insert({ user_id: user.id, plugin_id: pluginId, name: plugin?.name || 'Integration', integration_type: 'plugin' });
    if (error) toast.error('Failed to install');
    else { toast.success('Plugin installed'); fetchAll(); }
  };

  const uninstallIntegration = async (id: string) => {
    const { error } = await supabase.from('integrations').delete().eq('id', id);
    if (error) toast.error('Failed to uninstall');
    else { toast.success('Uninstalled'); fetchAll(); }
  };

  return { plugins, myPlugins, integrations, transactions, isLoading, createPlugin, publishPlugin, installPlugin, uninstallIntegration };
}
