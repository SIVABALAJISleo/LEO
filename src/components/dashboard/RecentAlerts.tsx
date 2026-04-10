import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Alert } from '@/lib/types';
import { AlertCircle, AlertTriangle, Info, XCircle, Check, Bell } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';
import { cn } from '@/lib/utils';
import { useToast } from '@/hooks/use-toast';

interface RecentAlertsProps {
  alerts: Alert[];
  onResolve: (alertId: string) => Promise<void>;
}

export const RecentAlerts = ({ alerts, onResolve }: RecentAlertsProps) => {
  const { toast } = useToast();

  const getSeverityConfig = (severity: string) => {
    switch (severity) {
      case 'critical':
        return {
          icon: XCircle,
          className: 'text-destructive bg-destructive/20 border-destructive/30',
          badge: 'bg-destructive text-destructive-foreground',
        };
      case 'error':
        return {
          icon: AlertCircle,
          className: 'text-red-500 bg-red-500/20 border-red-500/30',
          badge: 'bg-red-500 text-white',
        };
      case 'warning':
        return {
          icon: AlertTriangle,
          className: 'text-yellow-500 bg-yellow-500/20 border-yellow-500/30',
          badge: 'bg-yellow-500 text-yellow-900',
        };
      default:
        return {
          icon: Info,
          className: 'text-blue-500 bg-blue-500/20 border-blue-500/30',
          badge: 'bg-blue-500 text-white',
        };
    }
  };

  const handleResolve = async (alertId: string) => {
    try {
      await onResolve(alertId);
      toast({
        title: 'Alert Resolved',
        description: 'The alert has been marked as resolved.',
      });
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to resolve alert.',
        variant: 'destructive',
      });
    }
  };

  const unresolvedAlerts = alerts.filter(a => !a.resolved);

  return (
    <Card className="p-6 bg-card border-border">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold">Recent Alerts</h3>
        <Badge variant="secondary">
          {unresolvedAlerts.length} unresolved
        </Badge>
      </div>

      {alerts.length === 0 ? (
        <div className="text-center py-8 text-muted-foreground">
          <Bell className="h-8 w-8 mx-auto mb-2 opacity-50" />
          <p className="text-sm">No alerts</p>
        </div>
      ) : (
        <div className="space-y-3 max-h-[300px] overflow-y-auto">
          {alerts.map((alert) => {
            const config = getSeverityConfig(alert.severity);
            const SeverityIcon = config.icon;

            return (
              <div
                key={alert.id}
                className={cn(
                  'p-4 rounded-lg border transition-all',
                  alert.resolved ? 'opacity-60 bg-muted/20' : config.className
                )}
              >
                <div className="flex items-start gap-3">
                  <SeverityIcon className="h-5 w-5 flex-shrink-0 mt-0.5" />
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <h4 className="font-medium truncate">{alert.title}</h4>
                      <Badge className={cn('text-xs', config.badge)}>
                        {alert.severity}
                      </Badge>
                      {alert.resolved && (
                        <Badge variant="outline" className="text-xs text-primary">
                          Resolved
                        </Badge>
                      )}
                    </div>
                    <p className="text-sm text-muted-foreground line-clamp-2">
                      {alert.message}
                    </p>
                    <div className="flex items-center justify-between mt-2">
                      <span className="text-xs text-muted-foreground">
                        {formatDistanceToNow(new Date(alert.created_at), { addSuffix: true })}
                      </span>
                      {!alert.resolved && (
                        <Button
                          size="sm"
                          variant="ghost"
                          className="h-7 text-xs"
                          onClick={() => handleResolve(alert.id)}
                        >
                          <Check className="h-3 w-3 mr-1" />
                          Resolve
                        </Button>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </Card>
  );
};
