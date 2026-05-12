import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import {
  Zap,
  TrendingUp,
  Database,
  Clock,
  DollarSign,
  Activity,
  CheckCircle2,
  AlertTriangle,
  Server
} from 'lucide-react';
import { gpuSavingsTracker, GpuSavingsScore } from '@/lib/safeCompute/GpuSavingsTracker';

interface GpuSavingsScoreCardProps {
  className?: string;
  compact?: boolean;
}

export const GpuSavingsScoreCard = ({ className, compact = false }: GpuSavingsScoreCardProps) => {
  const [score, setScore] = useState<GpuSavingsScore | null>(null);

  useEffect(() => {
    // Initial load
    setScore(gpuSavingsTracker.getSavingsScore());

    // Update every 5 seconds
    const interval = setInterval(() => {
      setScore(gpuSavingsTracker.getSavingsScore());
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  if (!score) {
    return (
      <Card className={className}>
        <CardContent className="pt-6">
          <div className="text-muted-foreground text-sm">Loading efficiency metrics...</div>
        </CardContent>
      </Card>
    );
  }

  const overallEfficiency = score.computeAvoidedPercent + score.reusePercent;
  const efficiencyLevel = overallEfficiency >= 70 ? 'excellent' : overallEfficiency >= 40 ? 'good' : 'building';

  if (compact) {
    return (
      <Card className={className}>
        <CardContent className="pt-4 pb-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Zap className="h-4 w-4 text-green-500" />
              <span className="font-medium">GPU Efficiency</span>
            </div>
            <Badge variant={efficiencyLevel === 'excellent' ? 'default' : 'secondary'}>
              {overallEfficiency}%
            </Badge>
          </div>
          <Progress value={overallEfficiency} className="mt-2 h-2" />
          <div className="flex justify-between mt-2 text-xs text-muted-foreground">
            <span>{score.totalJobsProcessed} jobs processed</span>
            <span>${score.estimatedCostSaved} saved</span>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={className}>
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between gap-4">
          <div>
            <CardTitle className="flex items-center gap-2">
              <Zap className="h-5 w-5 text-green-500" />
              GPU Efficiency Score
            </CardTitle>
            <CardDescription>
              Real compute savings through intelligent orchestration
            </CardDescription>
          </div>
          <Badge
            variant={efficiencyLevel === 'excellent' ? 'default' : 'secondary'}
            className="text-lg px-3 py-1"
          >
            {overallEfficiency}%
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Main Progress */}
        <div>
          <div className="flex justify-between text-sm mb-1">
            <span className="text-muted-foreground">Overall Efficiency</span>
            <span className="font-medium">
              {efficiencyLevel === 'excellent' && <CheckCircle2 className="inline h-4 w-4 text-green-500 mr-1" />}
              {efficiencyLevel === 'building' && <AlertTriangle className="inline h-4 w-4 text-yellow-500 mr-1" />}
              {efficiencyLevel.charAt(0).toUpperCase() + efficiencyLevel.slice(1)}
            </span>
          </div>
          <Progress value={overallEfficiency} className="h-3" />
        </div>

        {/* Breakdown Grid */}
        <div className="grid grid-cols-2 gap-3">
          <div className="bg-muted/50 rounded-lg p-3">
            <div className="flex items-center gap-2 text-sm text-muted-foreground mb-1">
              <Activity className="h-4 w-4" />
              Compute Avoided
            </div>
            <div className="text-2xl font-bold">{score.computeAvoidedPercent}%</div>
            <div className="text-xs text-muted-foreground">{score.jobsAvoidedGpu} jobs</div>
          </div>

          <div className="bg-muted/50 rounded-lg p-3">
            <div className="flex items-center gap-2 text-sm text-muted-foreground mb-1">
              <Database className="h-4 w-4" />
              Cache/Reuse
            </div>
            <div className="text-2xl font-bold">{score.reusePercent}%</div>
            <div className="text-xs text-muted-foreground">{score.jobsFromCache + score.jobsCollapsed} hits</div>
          </div>

          <div className="bg-muted/50 rounded-lg p-3">
            <div className="flex items-center gap-2 text-sm text-muted-foreground mb-1">
              <TrendingUp className="h-4 w-4" />
              Safe Downgrades
            </div>
            <div className="text-2xl font-bold">{score.safeDowngradePercent}%</div>
            <div className="text-xs text-muted-foreground">{score.jobsDowngraded} jobs</div>
          </div>

          <div className="bg-muted/50 rounded-lg p-3">
            <div className="flex items-center gap-2 text-sm text-muted-foreground mb-1">
              <Server className="h-4 w-4" />
              Local Processing
            </div>
            <div className="text-2xl font-bold">{score.delegationPreventedPercent}%</div>
            <div className="text-xs text-muted-foreground">{score.totalJobsProcessed - score.jobsDelegated} local</div>
          </div>
        </div>

        {/* Impact Summary */}
        <div className="border-t pt-3">
          <div className="text-sm font-medium mb-2">Impact Summary</div>
          <div className="grid grid-cols-3 gap-2 text-center">
            <div>
              <div className="flex items-center justify-center gap-1 text-muted-foreground text-xs">
                <Clock className="h-3 w-3" />
                GPU Hours
              </div>
              <div className="font-bold text-green-600">{score.estimatedGpuHoursSaved}h saved</div>
            </div>
            <div>
              <div className="flex items-center justify-center gap-1 text-muted-foreground text-xs">
                <DollarSign className="h-3 w-3" />
                Cost
              </div>
              <div className="font-bold text-green-600">${score.estimatedCostSaved}</div>
            </div>
            <div>
              <div className="flex items-center justify-center gap-1 text-muted-foreground text-xs">
                <Zap className="h-3 w-3" />
                Multiplier
              </div>
              <div className="font-bold text-blue-600">{score.effectiveThroughputMultiplier}x</div>
            </div>
          </div>
        </div>

        {/* Quality Assurance */}
        <div className="flex items-center justify-between text-sm border-t pt-3">
          <span className="text-muted-foreground">Quality Score</span>
          <div className="flex items-center gap-2">
            <span className="font-medium">{score.averageQualityScore}</span>
            {score.qualityViolations > 0 && (
              <Badge variant="destructive" className="text-xs">
                {score.qualityViolations} violations
              </Badge>
            )}
          </div>
        </div>

        {/* Status Footer */}
        <div className="text-xs text-muted-foreground text-center pt-2 border-t">
          {score.totalJobsProcessed === 0 ? (
            'Awaiting workloads. Metrics will populate after job execution.'
          ) : (
            `${score.totalJobsProcessed} jobs analyzed • Updated ${new Date(score.lastUpdatedAt).toLocaleTimeString()}`
          )}
        </div>
      </CardContent>
    </Card>
  );
};

export default GpuSavingsScoreCard;
