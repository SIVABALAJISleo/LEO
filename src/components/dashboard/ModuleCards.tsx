import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { ModuleStatus } from '@/lib/types';
import { useNavigate } from 'react-router-dom';
import { Settings, CheckCircle, AlertTriangle, XCircle } from 'lucide-react';
import { cn } from '@/lib/utils';

interface ModuleCardsProps {
  statuses: ModuleStatus[];
  configs: Record<string, any>;
}

const MODULES = [
  { name: 'AdaptiveDowngrade', label: 'Adaptive Downgrade' },
  { name: 'ProgressiveCompute', label: 'Progressive Compute' },
  { name: 'TemporalReconstruction', label: 'Temporal Recon' },
  { name: 'PerceptualValidation', label: 'Perceptual Metric' },
  { name: 'MixtureOfExperts', label: 'MoE Router' },
  { name: 'SemanticCache', label: 'Semantic Caching' },
  { name: 'VectorSearch', label: 'Vector Retrieval' },
  { name: 'RateLimiting', label: 'API Governance' },
  { name: 'ChaosResilience', label: 'Expert Failure Recovery' },
  { name: 'HardwareBalancing', label: 'CPU/iGPU Balancer' },
  { name: 'TileSolver', label: 'Tile-Based Solver' },
  { name: 'ProbabilisticCore', label: 'Probabilistic Engine' },
  { name: 'AsyncOffload', label: 'Async Task Offload' },
  { name: 'SelfProfiling', label: 'Self-Profiling Opt' },
  { name: 'BehaviorEmulation', label: 'Behavioral Emulation' },
];

export const ModuleCards = ({ statuses, configs }: ModuleCardsProps) => {
  const navigate = useNavigate();

  const getStatusByName = (name: string) => {
    return statuses.find(s => s.module_name === name);
  };

  const getConfigByName = (name: string) => {
    return configs[name];
  };

  const getStatusIcon = (status: string | undefined) => {
    switch (status) {
      case 'operational':
      case 'idle':
        return <CheckCircle className="h-4 w-4 text-primary" />;
      case 'degraded':
      case 'warning':
        return <AlertTriangle className="h-4 w-4 text-yellow-500" />;
      case 'offline':
      case 'error':
        return <XCircle className="h-4 w-4 text-destructive" />;
      default:
        return <CheckCircle className="h-4 w-4 text-muted-foreground" />;
    }
  };

  const getStatusBadge = (status: string | undefined) => {
    switch (status) {
      case 'operational':
      case 'idle':
        return 'bg-primary/20 text-primary';
      case 'degraded':
      case 'warning':
        return 'bg-yellow-500/20 text-yellow-500';
      case 'offline':
      case 'error':
        return 'bg-destructive/20 text-destructive';
      default:
        return 'bg-muted text-muted-foreground';
    }
  };

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold">Optimization Modules</h3>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4">
        {MODULES.map((module) => {
          const status = getStatusByName(module.name);
          const config = getConfigByName(module.name);
          const healthScore = status?.health_score ?? 100;
          const speedup = config?.speedup_achieved;
          const compression = config?.compression_ratio_achieved;

          return (
            <Card
              key={module.name}
              className={cn(
                'p-4 bg-card border-border hover:border-primary/50 transition-all cursor-pointer group',
                config?.enabled === false && 'opacity-60'
              )}
              onClick={() => navigate('/dashboard/modules')}
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-2">
                  {getStatusIcon(status?.status)}
                  <Badge
                    variant="secondary"
                    className={cn('text-xs', getStatusBadge(status?.status))}
                  >
                    {status?.status || 'idle'}
                  </Badge>
                </div>
              </div>

              <h4 className="font-medium text-sm mb-2 group-hover:text-primary transition-colors">
                {module.label}
              </h4>

              {/* Health Score */}
              <div className="mb-2">
                <div className="flex justify-between text-xs text-muted-foreground mb-1">
                  <span>Health</span>
                  <span>{healthScore.toFixed(0)}%</span>
                </div>
                <div className="h-1 bg-muted rounded-full overflow-hidden">
                  <div
                    className={cn(
                      'h-full transition-all',
                      healthScore >= 80 ? 'bg-primary' :
                        healthScore >= 50 ? 'bg-yellow-500' : 'bg-destructive'
                    )}
                    style={{ width: `${healthScore}%` }}
                  />
                </div>
              </div>

              {/* Metrics */}
              <div className="flex justify-between text-xs">
                <div>
                  <span className="text-muted-foreground">Speedup:</span>
                  <span className="ml-1 font-medium text-primary">
                    {speedup ? `${(speedup * 100).toFixed(1)}%` : 'N/A'}
                  </span>
                </div>
                <div>
                  <span className="text-muted-foreground">Comp:</span>
                  <span className="ml-1 font-medium text-primary">
                    {compression ? `${(compression * 100).toFixed(1)}%` : 'N/A'}
                  </span>
                </div>
              </div>

              {/* Configure button */}
              <Button
                size="sm"
                variant="ghost"
                className="w-full mt-3 opacity-0 group-hover:opacity-100 transition-opacity"
                onClick={(e) => {
                  e.stopPropagation();
                  navigate('/dashboard/modules');
                }}
              >
                <Settings className="h-3 w-3 mr-1" />
                Configure
              </Button>
            </Card>
          );
        })}
      </div>
    </div>
  );
};
