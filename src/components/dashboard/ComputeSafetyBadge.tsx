import { Shield, CheckCircle, AlertTriangle, Flame, Wifi, WifiOff } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import { useSafeCompute } from '@/hooks/useSafeCompute';
import { cn } from '@/lib/utils';

export const ComputeSafetyBadge = () => {
  const { isEnabled, getThermalLevel, isOnline, getLoadStatus } = useSafeCompute();
  
  const thermalLevel = getThermalLevel();
  const loadStatus = getLoadStatus();
  
  const getStatusColor = () => {
    if (thermalLevel === 'emergency' || thermalLevel === 'critical') return 'bg-destructive text-destructive-foreground';
    if (thermalLevel === 'warning' || loadStatus === 'heavy') return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/50';
    return 'bg-primary/20 text-primary border-primary/50';
  };
  
  const getStatusLabel = () => {
    if (thermalLevel === 'emergency' || thermalLevel === 'critical') return 'High Load';
    if (thermalLevel === 'warning' || loadStatus === 'heavy') return 'Busy';
    return 'Ready';
  };
  
  const getStatusIcon = () => {
    if (thermalLevel === 'emergency' || thermalLevel === 'critical') {
      return <Flame className="h-3 w-3" />;
    }
    if (thermalLevel === 'warning') {
      return <AlertTriangle className="h-3 w-3" />;
    }
    return <CheckCircle className="h-3 w-3" />;
  };

  if (!isEnabled) return null;

  return (
    <TooltipProvider>
      <div className="flex items-center gap-2 flex-wrap">
        {/* Main Status Badge */}
        <Tooltip>
          <TooltipTrigger asChild>
            <Badge 
              variant="outline" 
              className={cn(
                'flex items-center gap-1.5 px-2 py-1 font-medium transition-colors',
                getStatusColor()
              )}
            >
              <Shield className="h-3 w-3" />
              <span className="text-xs">{getStatusLabel()}</span>
              {getStatusIcon()}
            </Badge>
          </TooltipTrigger>
          <TooltipContent side="bottom" className="max-w-xs">
            <div className="space-y-1">
              <p className="font-semibold">System Status</p>
              <p className="text-xs text-muted-foreground">
                Your jobs are processed securely and efficiently.
              </p>
            </div>
          </TooltipContent>
        </Tooltip>
        
        {/* Online Status */}
        <Tooltip>
          <TooltipTrigger asChild>
            <Badge 
              variant="outline" 
              className={cn(
                'flex items-center gap-1 px-2 py-1',
                isOnline 
                  ? 'bg-primary/10 text-primary border-primary/30' 
                  : 'bg-yellow-500/10 text-yellow-500 border-yellow-500/30'
              )}
            >
              {isOnline ? <Wifi className="h-3 w-3" /> : <WifiOff className="h-3 w-3" />}
              <span className="text-xs">{isOnline ? 'Online' : 'Offline'}</span>
            </Badge>
          </TooltipTrigger>
          <TooltipContent side="bottom">
            {isOnline ? 'Connected and syncing' : 'Working offline - will sync when connected'}
          </TooltipContent>
        </Tooltip>
      </div>
    </TooltipProvider>
  );
};
