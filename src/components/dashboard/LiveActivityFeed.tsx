/**
 * Live Activity Feed - Shows real-time system activity
 * Professional-grade activity stream component
 */

import { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import { Button } from '@/components/ui/button';
import { 
  Activity, 
  Zap, 
  CheckCircle2, 
  XCircle, 
  AlertTriangle,
  Clock,
  Server,
  Cpu,
  RefreshCw,
  Filter
} from 'lucide-react';
import { firebaseClient as supabase } from '@/integrations/firebase/client';
import { useAuth } from '@/contexts/AuthContext';
import { formatDistanceToNow } from 'date-fns';
import { cn } from '@/lib/utils';

interface ActivityItem {
  id: string;
  type: 'job_created' | 'job_started' | 'job_completed' | 'job_failed' | 'alert' | 'system';
  title: string;
  description: string;
  timestamp: string;
  metadata?: Record<string, any>;
}

interface LiveActivityFeedProps {
  className?: string;
  maxItems?: number;
}

const ACTIVITY_ICONS: Record<ActivityItem['type'], typeof Zap> = {
  job_created: Zap,
  job_started: Cpu,
  job_completed: CheckCircle2,
  job_failed: XCircle,
  alert: AlertTriangle,
  system: Server,
};

const ACTIVITY_COLORS: Record<ActivityItem['type'], string> = {
  job_created: 'text-blue-500 bg-blue-500/10',
  job_started: 'text-purple-500 bg-purple-500/10',
  job_completed: 'text-green-500 bg-green-500/10',
  job_failed: 'text-red-500 bg-red-500/10',
  alert: 'text-yellow-500 bg-yellow-500/10',
  system: 'text-cyan-500 bg-cyan-500/10',
};

export const LiveActivityFeed = ({ className, maxItems = 20 }: LiveActivityFeedProps) => {
  const { user } = useAuth();
  const [activities, setActivities] = useState<ActivityItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<'all' | 'jobs' | 'alerts'>('all');

  const fetchRecentActivity = useCallback(async () => {
    if (!user) return;

    try {
      setLoading(true);

      // Fetch recent jobs
      const { data: jobs } = await supabase
        .from('inference_jobs')
        .select('id, status, created_at, updated_at, model_id')
        .eq('user_id', user.id)
        .order('updated_at', { ascending: false })
        .limit(10);

      // Fetch recent alerts
      const { data: alerts } = await supabase
        .from('alerts')
        .select('id, title, message, severity, created_at')
        .eq('user_id', user.id)
        .order('created_at', { ascending: false })
        .limit(10);

      const jobActivities: ActivityItem[] = (jobs || []).map(job => ({
        id: `job-${job.id}`,
        type: job.status === 'completed' ? 'job_completed' 
            : job.status === 'failed' ? 'job_failed'
            : job.status === 'running' ? 'job_started'
            : 'job_created',
        title: `Job ${job.id.substring(0, 8)}`,
        description: `Status: ${job.status}`,
        timestamp: job.updated_at || job.created_at,
      }));

      const alertActivities: ActivityItem[] = (alerts || []).map(alert => ({
        id: `alert-${alert.id}`,
        type: 'alert',
        title: alert.title,
        description: alert.message,
        timestamp: alert.created_at,
        metadata: { severity: alert.severity },
      }));

      // Combine and sort by timestamp
      const combined = [...jobActivities, ...alertActivities]
        .sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())
        .slice(0, maxItems);

      setActivities(combined);
    } catch (error) {
      console.error('Error fetching activity:', error);
    } finally {
      setLoading(false);
    }
  }, [user, maxItems]);

  useEffect(() => {
    fetchRecentActivity();
  }, [fetchRecentActivity]);

  // Real-time subscription
  useEffect(() => {
    if (!user) return;

    const channel = supabase
      .channel('activity-feed')
      .on(
        'postgres_changes',
        { event: '*', schema: 'public', table: 'inference_jobs', filter: `user_id=eq.${user.id}` },
        () => fetchRecentActivity()
      )
      .on(
        'postgres_changes',
        { event: 'INSERT', schema: 'public', table: 'alerts', filter: `user_id=eq.${user.id}` },
        () => fetchRecentActivity()
      )
      .subscribe();

    return () => {
      supabase.removeChannel(channel);
    };
  }, [user, fetchRecentActivity]);

  const filteredActivities = activities.filter(a => {
    if (filter === 'all') return true;
    if (filter === 'jobs') return a.type.startsWith('job_');
    if (filter === 'alerts') return a.type === 'alert';
    return true;
  });

  return (
    <Card className={cn('bg-card border-border', className)}>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2 text-lg">
            <Activity className="h-5 w-5 text-primary" />
            Live Activity
            <Badge variant="outline" className="ml-2 font-mono text-xs">
              {filteredActivities.length}
            </Badge>
          </CardTitle>
          <div className="flex items-center gap-2">
            <Button
              variant="ghost"
              size="icon"
              onClick={fetchRecentActivity}
              disabled={loading}
            >
              <RefreshCw className={cn('h-4 w-4', loading && 'animate-spin')} />
            </Button>
          </div>
        </div>
        <div className="flex gap-1 mt-2">
          {(['all', 'jobs', 'alerts'] as const).map(f => (
            <Button
              key={f}
              size="sm"
              variant={filter === f ? 'default' : 'ghost'}
              onClick={() => setFilter(f)}
              className="h-7 text-xs"
            >
              {f.charAt(0).toUpperCase() + f.slice(1)}
            </Button>
          ))}
        </div>
      </CardHeader>
      <CardContent>
        <ScrollArea className="h-[300px] pr-4">
          {loading && activities.length === 0 ? (
            <div className="flex items-center justify-center h-full text-muted-foreground">
              <RefreshCw className="h-5 w-5 animate-spin mr-2" />
              Loading activity...
            </div>
          ) : filteredActivities.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-muted-foreground">
              <Activity className="h-10 w-10 mb-2 opacity-50" />
              <p>No recent activity</p>
            </div>
          ) : (
            <div className="space-y-3">
              {filteredActivities.map((activity, idx) => {
                const Icon = ACTIVITY_ICONS[activity.type];
                const colorClass = ACTIVITY_COLORS[activity.type];
                
                return (
                  <div key={activity.id}>
                    <div className="flex items-start gap-3">
                      <div className={cn('p-2 rounded-lg', colorClass)}>
                        <Icon className="h-4 w-4" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between gap-2">
                          <p className="font-medium text-sm truncate">{activity.title}</p>
                          <span className="flex items-center text-xs text-muted-foreground whitespace-nowrap">
                            <Clock className="h-3 w-3 mr-1" />
                            {formatDistanceToNow(new Date(activity.timestamp), { addSuffix: true })}
                          </span>
                        </div>
                        <p className="text-xs text-muted-foreground truncate mt-0.5">
                          {activity.description}
                        </p>
                      </div>
                    </div>
                    {idx < filteredActivities.length - 1 && (
                      <Separator className="my-3" />
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </ScrollArea>
      </CardContent>
    </Card>
  );
};

export default LiveActivityFeed;
