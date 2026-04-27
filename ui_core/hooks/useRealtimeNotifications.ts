// eslint-disable-next-line @typescript-eslint/no-unused-vars
import { useEffect, useRef } from 'react';
import { toast } from 'sonner';
import { useAuth } from '@/contexts/AuthContext';
import { firebaseClient as supabase } from '@/integrations/firebase/client';
import { useNotifications } from '@/contexts/NotificationContext';

interface NotificationOptions {
  enableJobNotifications?: boolean;
  enableAlertNotifications?: boolean;
  enableSystemNotifications?: boolean;
  soundEnabled?: boolean;
}

export function useRealtimeNotifications(options: NotificationOptions = {}) {
  const { user } = useAuth();
  const { addNotification } = useNotifications();
  const {
    enableJobNotifications = true,
    enableAlertNotifications = true,
    enableSystemNotifications = true,
  } = options;

  useEffect(() => {
    if (!user) return;

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const channels: any[] = [];

    // Job status change notifications
    if (enableJobNotifications) {
      const jobChannel = supabase
        .channel('job-notifications')
        .on(
          'postgres_changes',
          {
            event: 'UPDATE',
            schema: 'public',
            table: 'inference_jobs',
            filter: `user_id=eq.${user.id}`,
          },
          // eslint-disable-next-line @typescript-eslint/no-explicit-any
          (payload: any) => {
            const newJob = payload.new as Record<string, unknown>;
            const oldJob = payload.old as Record<string, unknown>;

            if (newJob.status !== oldJob?.status) {
              const jobId = String(newJob.id || 'Unknown').substring(0, 8);
              let message = '';
              let severity: 'info' | 'warning' | 'error' | 'critical' = 'info';

              switch (newJob.status) {
                case 'running':
                  message = `Job ${jobId} started processing`;
                  toast.info(message);
                  break;
                case 'completed':
                  message = `Job ${jobId} completed successfully`;
                  toast.success(message);
                  break;
                case 'failed':
                  message = `Job ${jobId} failed`;
                  severity = 'error';
                  toast.error(`${message}: ${newJob.error_message || 'Unknown error'}`);
                  break;
                case 'cancelled':
                  message = `Job ${jobId} was cancelled`;
                  severity = 'warning';
                  toast.warning(message);
                  break;
              }

              if (message) {
                addNotification({
                  title: 'Job Update',
                  message,
                  severity,
                  alert_type: 'job'
                });
              }
            }
          }
        )
        .subscribe();

      channels.push(jobChannel);
    }

    // Alert notifications
    if (enableAlertNotifications) {
      const alertChannel = supabase
        .channel('alert-notifications')
        .on(
          'postgres_changes',
          {
            event: 'INSERT',
            schema: 'public',
            table: 'alerts',
            filter: `user_id=eq.${user.id}`,
          },
          // eslint-disable-next-line @typescript-eslint/no-explicit-any
          (payload: any) => {
            const alert = payload.new as Record<string, unknown>;

            const severity = String(alert.severity || 'info') as 'info' | 'warning' | 'error' | 'critical';
            const title = String(alert.title || 'Alert');
            const message = String(alert.message || '');

            addNotification({
              title,
              message,
              severity,
              alert_type: 'system'
            });

            if (severity === 'critical' || severity === 'error') {
              toast.error(title, {
                description: message,
                duration: 10000,
              });
            } else if (severity === 'warning') {
              toast.warning(title, {
                description: message,
                duration: 6000,
              });
            } else {
              toast.info(title, {
                description: message,
                duration: 6000,
              });
            }
          }
        )
        .subscribe();

      channels.push(alertChannel);
    }

    // System-wide notifications
    if (enableSystemNotifications) {
      const systemChannel = supabase
        .channel('system-notifications')
        .on(
          'postgres_changes',
          {
            event: 'INSERT',
            schema: 'public',
            table: 'system_metrics',
            filter: `user_id=eq.${user.id}`,
          },
          // eslint-disable-next-line @typescript-eslint/no-explicit-any
          (payload: any) => {
            const metrics = payload.new as Record<string, unknown>;

            // Only notify on critical status changes
            if (metrics.status === 'critical') {
              const title = 'System Critical Alert';
              const message = 'System health has dropped to critical levels. Check monitoring dashboard.';

              addNotification({
                title,
                message,
                severity: 'critical',
                alert_type: 'system'
              });

              toast.error(title, {
                description: message,
                duration: 10000,
              });
            }
          }
        )
        .subscribe();

      channels.push(systemChannel);
    }

    return () => {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      channels.forEach((channel: any) => {
        if (channel && typeof channel.unsubscribe === 'function') {
          channel.unsubscribe();
        } else {
          supabase.removeChannel(channel);
        }
      });
    };
  }, [user, enableJobNotifications, enableAlertNotifications, enableSystemNotifications, addNotification]);
}

export default useRealtimeNotifications;
