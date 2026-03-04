import { useState, useEffect } from 'react';
import { firebaseClient as supabase } from '@/integrations/firebase/client';
import { useAuth } from '@/contexts/AuthContext';
import { toast } from 'sonner';

export const VISUALIZATION_TYPES = [
  { value: 'sankey', label: 'Sankey Diagram' },
  { value: 'treemap', label: 'Treemap' },
  { value: 'network', label: 'Network Graph' },
  { value: 'heatmap', label: 'Heatmap' },
  { value: 'scatter', label: 'Scatter Plot' },
  { value: 'bar', label: 'Bar Chart' },
  { value: 'line', label: 'Line Chart' },
];

export function useAdvancedAnalyticsData() {
  const { user } = useAuth();
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [reports, setReports] = useState<any[]>([]);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [dashboards, setDashboards] = useState<any[]>([]);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [visualizations, setVisualizations] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (user) fetchAll();
  }, [user]);

  const fetchAll = async () => {
    setIsLoading(true);
    const [reportsRes, dashboardsRes, vizRes] = await Promise.all([
      supabase.from('analytics_reports').select('*').order('created_at', { ascending: false }),
      supabase.from('analytics_dashboards').select('*').order('created_at', { ascending: false }),
      supabase.from('custom_visualizations').select('*').order('created_at', { ascending: false }),
    ]);
    if (reportsRes.data) setReports(reportsRes.data);
    if (dashboardsRes.data) setDashboards(dashboardsRes.data);
    if (vizRes.data) setVisualizations(vizRes.data);
    setIsLoading(false);
  };

  const createReport = async (data: { name: string; report_type: string; description?: string }) => {
    if (!user) return;
    const { error } = await supabase.from('analytics_reports').insert({ ...data, user_id: user.id });
    if (error) toast.error('Failed to create report');
    else { toast.success('Report created'); fetchAll(); }
  };

  const createDashboard = async (data: { name: string; description?: string }) => {
    if (!user) return;
    const { error } = await supabase.from('analytics_dashboards').insert({ ...data, user_id: user.id });
    if (error) toast.error('Failed to create dashboard');
    else { toast.success('Dashboard created'); fetchAll(); }
  };

  const createVisualization = async (data: { name: string; visualization_type: string; dashboard_id?: string }) => {
    if (!user) return;
    const { error } = await supabase.from('custom_visualizations').insert({ ...data, user_id: user.id });
    if (error) toast.error('Failed to create visualization');
    else { toast.success('Visualization created'); fetchAll(); }
  };

  const deleteReport = async (id: string) => {
    const { error } = await supabase.from('analytics_reports').delete().eq('id', id);
    if (error) toast.error('Failed to delete');
    else { toast.success('Deleted'); fetchAll(); }
  };

  return { reports, dashboards, visualizations, isLoading, createReport, createDashboard, createVisualization, deleteReport };
}
