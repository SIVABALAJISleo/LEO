/**
 * WorkloadDelegationBanner - Shows execution target for jobs
 * 
 * PRODUCTION HONESTY:
 * - Clearly shows WHERE jobs will execute
 * - Never claims local GPU execution when none exists
 * - Explicitly marks delegated workloads
 */

import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Server, Cloud, Laptop, AlertTriangle, Info } from 'lucide-react';
import { cn } from '@/lib/utils';

export type ExecutionTarget = 'local' | 'cloud' | 'external' | 'pending' | 'unavailable';

interface WorkloadDelegationBannerProps {
  executionTarget: ExecutionTarget;
  deviceName?: string;
  className?: string;
}

const targetConfig: Record<ExecutionTarget, {
  icon: typeof Server;
  label: string;
  description: string;
  variant: 'default' | 'destructive';
  badgeVariant: 'default' | 'secondary' | 'destructive' | 'outline';
}> = {
  local: {
    icon: Laptop,
    label: 'Local Execution',
    description: 'Running on your local machine via installed agent',
    variant: 'default',
    badgeVariant: 'default',
  },
  cloud: {
    icon: Cloud,
    label: 'Cloud Delegated',
    description: 'Executing on cloud GPU infrastructure',
    variant: 'default',
    badgeVariant: 'secondary',
  },
  external: {
    icon: Server,
    label: 'External GPU',
    description: 'Running on your registered external GPU',
    variant: 'default',
    badgeVariant: 'secondary',
  },
  pending: {
    icon: Info,
    label: 'Awaiting Assignment',
    description: 'Job queued - waiting for available compute resource',
    variant: 'default',
    badgeVariant: 'outline',
  },
  unavailable: {
    icon: AlertTriangle,
    label: 'No Compute Available',
    description: 'No devices available. Connect a local agent or external GPU.',
    variant: 'destructive',
    badgeVariant: 'destructive',
  },
};

export const WorkloadDelegationBanner = ({ 
  executionTarget, 
  deviceName,
  className 
}: WorkloadDelegationBannerProps) => {
  const config = targetConfig[executionTarget];
  const Icon = config.icon;

  return (
    <Alert variant={config.variant} className={cn(className)}>
      <Icon className="h-4 w-4" />
      <AlertTitle className="flex items-center gap-2">
        {config.label}
        <Badge variant={config.badgeVariant}>{executionTarget.toUpperCase()}</Badge>
      </AlertTitle>
      <AlertDescription>
        {config.description}
        {deviceName && (
          <span className="block text-xs mt-1 text-muted-foreground">
            Device: {deviceName}
          </span>
        )}
      </AlertDescription>
    </Alert>
  );
};

/**
 * ExecutionTargetBadge - Compact badge showing execution target
 */
export const ExecutionTargetBadge = ({ 
  target, 
  deviceName,
  className 
}: { 
  target: ExecutionTarget; 
  deviceName?: string;
  className?: string;
}) => {
  const config = targetConfig[target];
  const Icon = config.icon;

  return (
    <Badge variant={config.badgeVariant} className={cn('gap-1.5', className)}>
      <Icon className="h-3 w-3" />
      {target === 'pending' ? 'Pending' : deviceName || config.label}
    </Badge>
  );
};

export default WorkloadDelegationBanner;
