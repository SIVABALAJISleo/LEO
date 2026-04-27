import { useState, useEffect } from 'react';
import { firebaseClient as supabase } from '@/integrations/firebase/client';
import { useAuth } from '@/contexts/AuthContext';
import { toast } from 'sonner';

export function usePersonalizationData() {
  const { user } = useAuth();
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [behaviors, setBehaviors] = useState<any[]>([]);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [settings, setSettings] = useState<any | null>(null);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [recommendations, setRecommendations] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (user) fetchAll();
  }, [user]);

  const fetchAll = async () => {
    setIsLoading(true);
    const [behaviorRes, settingsRes, recsRes] = await Promise.all([
      supabase.from('user_behaviors').select('*').order('recorded_at', { ascending: false }).limit(50),
      supabase.from('personalization_settings').select('*').single(),
      supabase.from('recommendations').select('*').eq('is_dismissed', false).order('priority', { ascending: true }),
    ]);
    if (behaviorRes.data) setBehaviors(behaviorRes.data);
    if (settingsRes.data) setSettings(settingsRes.data);
    if (recsRes.data) setRecommendations(recsRes.data);
    setIsLoading(false);
  };

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const trackBehavior = async (behaviorType: string, action: string, target?: string, metadata?: any) => {
    if (!user) return;
    await supabase.from('user_behaviors').insert({ user_id: user.id, behavior_type: behaviorType, action, target, metadata });
  };

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const updateSettings = async (data: Partial<any>) => {
    if (!user) return;
    if (settings) {
      const { error } = await supabase.from('personalization_settings').update({ ...data, updated_at: new Date().toISOString() }).eq('user_id', user.id);
      if (error) toast.error('Failed to update');
      else { toast.success('Settings updated'); fetchAll(); }
    } else {
      const { error } = await supabase.from('personalization_settings').insert({ ...data, user_id: user.id });
      if (error) toast.error('Failed to save');
      else { toast.success('Settings saved'); fetchAll(); }
    }
  };

  const dismissRecommendation = async (id: string) => {
    const { error } = await supabase.from('recommendations').update({ is_dismissed: true, dismissed_at: new Date().toISOString() }).eq('id', id);
    if (error) toast.error('Failed to dismiss');
    else fetchAll();
  };

  return { behaviors, settings, recommendations, isLoading, trackBehavior, updateSettings, dismissRecommendation };
}
