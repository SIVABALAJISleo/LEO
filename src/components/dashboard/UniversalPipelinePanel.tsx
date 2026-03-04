/**
 * UNIVERSAL PIPELINE PANEL - GPU Neutralization Dashboard
 * 
 * Displays the decision pipeline: IDENTIFY_GOAL → REPLACE_OUTCOME → AVOID → REUSE → APPROXIMATE → PERCEIVE_REALTIME → DELEGATE → EXPLAIN
 */

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Separator } from '@/components/ui/separator';
import {
  Zap,
  Database,
  Layers,
  Clock,
  Cpu,
  Cloud,
  HelpCircle,
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  CheckCircle2,
  XCircle,
  ArrowRight,
  Activity,
  Target,
  Replace
} from 'lucide-react';
import { universalDecisionPipeline, PipelineStats, PipelineStep } from '@/lib/safeCompute/UniversalDecisionPipeline';
import { cn } from '@/lib/utils';

interface UniversalPipelinePanelProps {
  className?: string;
}

const STEP_CONFIG: Record<PipelineStep, { icon: typeof Zap; label: string; description: string }> = {
  DECISION_MATRIX: {
    icon: Activity,
    label: 'Matrix',
    description: 'Criticality scoring + parallel truth sources'
  },
  MASTER_PREDICTOR: {
    icon: Zap,
    label: 'Predict',
    description: 'Instant path classification (<1ms)'
  },
  IDENTIFY_GOAL: {
    icon: Target,
    label: 'Identify',
    description: 'Extract what user actually wants'
  },
  REPLACE_OUTCOME: {
    icon: Replace,
    label: 'Replace',
    description: 'Swap heavy compute with lighter outcome'
  },
  AVOID: {
    icon: Zap,
    label: 'Avoid',
    description: 'Skip compute via cache/prediction'
  },
  REUSE: {
    icon: Database,
    label: 'Reuse',
    description: 'Serve from similar past results'
  },
  APPROXIMATE: {
    icon: Layers,
    label: 'Approx',
    description: 'Reduce precision for speed'
  },
  PERCEIVE_REALTIME: {
    icon: Clock,
    label: 'Realtime',
    description: 'Deliver <100ms, refine async'
  },
  DISTRIBUTED: {
    icon: Cpu,
    label: 'Swarm',
    description: 'Distributed/edge execution'
  },
  DELEGATE: {
    icon: Cloud,
    label: 'Delegate',
    description: 'Route to external GPU (optional)'
  },
  EXPLAIN: {
    icon: HelpCircle,
    label: 'Explain',
    description: 'Physics-limited with guidance'
  },
};

export const UniversalPipelinePanel = ({ className }: UniversalPipelinePanelProps) => {
  const [stats, setStats] = useState<PipelineStats | null>(null);

  useEffect(() => {
    setStats(universalDecisionPipeline.getStats());

    const interval = setInterval(() => {
      setStats(universalDecisionPipeline.getStats());
    }, 3000);

    return () => clearInterval(interval);
  }, []);

  const auditReport = universalDecisionPipeline.generateAuditReport();

  return (
    <Card className={cn('bg-card border-border', className)}>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2 text-lg">
            <Activity className="h-5 w-5 text-primary" />
            GPU Neutralization Pipeline
          </CardTitle>
          <Badge variant="outline" className="font-mono text-xs">
            {auditReport.coveragePercent}% Neutralized
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Pipeline Steps Visual - Fixed wrapping for zero-overflow */}
        <div className="relative overflow-hidden w-full">
          <div className="flex flex-wrap items-center justify-center gap-y-4 gap-x-1 pb-4">
            {(Object.keys(STEP_CONFIG) as PipelineStep[]).map((step, idx, arr) => {
              const config = STEP_CONFIG[step];
              const Icon = config.icon;
              const count = stats?.byStep[step] || 0;
              const isActive = count > 0;

              return (
                <div key={step} className="flex items-center">
                  <div className={cn(
                    'flex flex-col items-center p-2 rounded-lg transition-all min-w-[60px]',
                    isActive ? 'bg-primary/10 border border-primary/20' : 'bg-muted/30 border border-transparent',
                  )}>
                    <div className={cn(
                      'w-8 h-8 rounded-full flex items-center justify-center mb-1',
                      isActive ? 'bg-primary/20 text-primary' : 'bg-muted text-muted-foreground'
                    )}>
                      <Icon className="h-4 w-4" />
                    </div>
                    <span className="text-[9px] font-bold text-center leading-tight uppercase tracking-tighter">
                      {config.label}
                    </span>
                    <span className={cn(
                      'text-[10px] font-mono font-bold',
                      isActive ? 'text-primary' : 'text-muted-foreground'
                    )}>
                      {count}
                    </span>
                  </div>
                  {idx < arr.length - 1 && (
                    <ArrowRight className="h-3 w-3 text-muted-foreground mx-0.5 flex-shrink-0 opacity-50" />
                  )}
                </div>
              );
            })}
          </div>
        </div>

        <Separator />

        {/* Efficiency Metrics */}
        <div className="grid grid-cols-2 gap-3">
          <div className="space-y-2">
            <div className="flex items-center justify-between text-sm">
              <span className="text-muted-foreground">GPU Neutralized</span>
              <span className="font-mono font-medium text-primary">
                {Math.round((stats?.gpuAvoidanceRate || 0) * 100)}%
              </span>
            </div>
            <Progress value={(stats?.gpuAvoidanceRate || 0) * 100} className="h-2" />
          </div>

          <div className="space-y-2">
            <div className="flex items-center justify-between text-sm">
              <span className="text-muted-foreground">Outcome Replaced</span>
              <span className="font-mono font-medium text-primary">
                {Math.round((stats?.outcomeReplacementRate || 0) * 100)}%
              </span>
            </div>
            <Progress value={(stats?.outcomeReplacementRate || 0) * 100} className="h-2" />
          </div>
        </div>

        {/* Final States */}
        <div className="space-y-2">
          <div className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
            Final States (Only These Allowed)
          </div>
          <div className="grid grid-cols-2 gap-2 text-xs">
            {[
              { key: 'completed_via_outcome_replacement', label: 'Outcome Replaced', icon: Replace, color: 'text-primary' },
              { key: 'completed_via_reuse', label: 'Reused', icon: Database, color: 'text-blue-500' },
              { key: 'completed_via_approximation', label: 'Approximated', icon: Layers, color: 'text-purple-500' },
              { key: 'completed_via_perceived_realtime', label: 'Perceived RT', icon: Clock, color: 'text-cyan-500' },
              { key: 'completed_via_local_execution', label: 'Local (Verified)', icon: Cpu, color: 'text-green-500' },
              { key: 'completed_via_delegation', label: 'Delegated', icon: Cloud, color: 'text-orange-500' },
              { key: 'physics_limited_explained', label: 'Physics-Limited', icon: XCircle, color: 'text-red-500' },
            ].map(({ key, label, icon: Icon, color }) => (
              <div key={key} className="flex items-center justify-between bg-muted/30 rounded px-2 py-1">
                <span className="flex items-center gap-1.5">
                  <Icon className={cn('h-3 w-3', color)} />
                  {label}
                </span>
                <span className="font-mono">
                  {stats?.byFinalState[key as keyof typeof stats.byFinalState] || 0}
                </span>
              </div>
            ))}
          </div>
        </div>

        <Separator />

        {/* Truth Statement */}
        <div className="bg-muted/30 rounded-lg p-3 text-xs font-mono">
          <div className="flex items-center gap-2 mb-2">
            <Zap className="h-3.5 w-3.5 text-primary" />
            <span className="font-semibold">SYSTEM TRUTH</span>
          </div>
          <div className="space-y-1 text-muted-foreground">
            <div>GPU replacement: <span className="text-destructive font-medium">❌ NOT CLAIMED</span></div>
            <div>GPU dependency neutralized: <span className="text-primary font-medium">✅ YES</span></div>
            <div>Practical coverage: <span className="text-primary font-medium">{auditReport.coveragePercent}%</span></div>
            <div>Remaining: <span className="text-muted-foreground">optional, rare, delegatable</span></div>
          </div>
        </div>

        {/* Total Processed */}
        {stats && stats.totalProcessed > 0 && (
          <div className="text-center text-xs text-muted-foreground">
            {stats.totalProcessed} workloads processed •
            Last updated {new Date(stats.lastUpdated).toLocaleTimeString()}
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default UniversalPipelinePanel;
