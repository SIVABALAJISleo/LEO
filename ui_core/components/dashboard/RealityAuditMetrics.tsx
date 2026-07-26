import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import {
  Activity,
  Eye,
  Shield,
  Cpu,
  Brain,
  RefreshCw,
  ArrowRight,
  AlertTriangle,
  CheckCircle2,
  Zap,
  TrendingUp,
  Clock,
  Database,
} from "lucide-react";
import {
  realityMinimizationEngine,
  realityReconciliationLayer,
  truthWeightScorer,
} from "@/lib/safeCompute";

export function RealityAuditMetrics({ className }: { className?: string }) {
  const [stats, setStats] = useState(realityMinimizationEngine.getStats());
  const [reconciliationStats, setReconciliationStats] = useState(
    realityReconciliationLayer.getStats(),
  );
  const [scorerStats, setScorerStats] = useState(truthWeightScorer.getStats());
  const [recentCorrections, setRecentCorrections] = useState(
    realityReconciliationLayer.getRecentCorrections(5),
  );

  useEffect(() => {
    const interval = setInterval(() => {
      setStats(realityMinimizationEngine.getStats());
      setReconciliationStats(realityReconciliationLayer.getStats());
      setScorerStats(truthWeightScorer.getStats());
      setRecentCorrections(realityReconciliationLayer.getRecentCorrections(5));
    }, 3000);
    return () => clearInterval(interval);
  }, []);

  const assertion = realityMinimizationEngine.getSystemAssertion();

  return (
    <Card className={className}>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg flex items-center gap-2">
            <Activity className="h-5 w-5 text-primary" />
            Reality Audit Metrics
          </CardTitle>
          <div className="flex gap-2">
            <Badge variant="outline" className="bg-green-500/10 text-green-600">
              {stats.coveragePercent.toFixed(1)}% Coverage
            </Badge>
            <Badge variant="outline" className="bg-yellow-500/10 text-yellow-600">
              {stats.authorityLockedPercent.toFixed(1)}% Authority-Locked
            </Badge>
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Execution Path Distribution */}
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
          <MetricBox
            icon={<Zap className="h-4 w-4 text-purple-500" />}
            label="Inferred"
            value={stats.tasksInferred}
            color="text-purple-500"
          />
          <MetricBox
            icon={<RefreshCw className="h-4 w-4 text-green-500" />}
            label="Reused"
            value={stats.tasksReused}
            color="text-green-500"
          />
          <MetricBox
            icon={<Brain className="h-4 w-4 text-blue-500" />}
            label="Predicted"
            value={stats.tasksPredicted}
            color="text-blue-500"
          />
          <MetricBox
            icon={<ArrowRight className="h-4 w-4 text-orange-500" />}
            label="Delegated"
            value={stats.tasksDelegated}
            color="text-orange-500"
          />
          <MetricBox
            icon={<Cpu className="h-4 w-4 text-red-500" />}
            label="Exact Compute"
            value={stats.tasksExactCompute}
            color="text-red-500"
          />
          <MetricBox
            icon={<Shield className="h-4 w-4 text-yellow-500" />}
            label="Authority Locked"
            value={stats.tasksAuthorityLocked}
            color="text-yellow-500"
          />
        </div>

        {/* Progress Bars */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-muted-foreground flex items-center gap-1">
                <Database className="h-3 w-3" />
                GPU Compute Avoided
              </span>
              <span className="font-medium">
                {stats.gpuComputeAvoided}/{stats.totalTasks} tasks
              </span>
            </div>
            <Progress
              value={stats.totalTasks > 0 ? (stats.gpuComputeAvoided / stats.totalTasks) * 100 : 0}
              className="h-2"
            />
          </div>
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-muted-foreground flex items-center gap-1">
                <TrendingUp className="h-3 w-3" />
                Reconciliation Success Rate
              </span>
              <span className="font-medium">
                {(reconciliationStats.successRate * 100).toFixed(1)}%
              </span>
            </div>
            <Progress value={reconciliationStats.successRate * 100} className="h-2" />
          </div>
        </div>

        {/* Truth-Weight Scoring Stats */}
        <div className="grid grid-cols-3 gap-4 p-3 bg-muted/30 rounded-lg">
          <div className="text-center">
            <p className="text-2xl font-bold">{scorerStats.totalScored}</p>
            <p className="text-xs text-muted-foreground">Tasks Scored</p>
          </div>
          <div className="text-center">
            <p className="text-2xl font-bold text-red-500">{scorerStats.criticalCount}</p>
            <p className="text-xs text-muted-foreground">Critical</p>
          </div>
          <div className="text-center">
            <p className="text-2xl font-bold text-green-500">{scorerStats.nonCriticalCount}</p>
            <p className="text-xs text-muted-foreground">Non-Critical</p>
          </div>
        </div>

        {/* Reconciliation Details */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <StatBadge
            label="Elastic Corrections"
            value={reconciliationStats.elasticCorrections}
            variant="default"
          />
          <StatBadge
            label="Temporal Smoothings"
            value={reconciliationStats.temporalSmoothings}
            variant="secondary"
          />
          <StatBadge
            label="Safe Rollbacks"
            value={reconciliationStats.safeRollbacks}
            variant="outline"
          />
          <StatBadge
            label="Execution Halts"
            value={reconciliationStats.executionHalts}
            variant="destructive"
          />
        </div>

        {/* Recent Corrections Log */}
        {recentCorrections.length > 0 && (
          <div className="space-y-2">
            <h4 className="text-sm font-medium flex items-center gap-1">
              <Clock className="h-3 w-3" />
              Recent Corrections (Visible & Logged)
            </h4>
            <div className="space-y-1 max-h-32 overflow-y-auto">
              {recentCorrections.map((correction, i) => (
                <div
                  key={i}
                  className="flex items-center justify-between text-xs p-2 bg-muted/20 rounded"
                >
                  <span className="truncate max-w-[200px]">{correction.taskId}</span>
                  <Badge variant="outline" className="text-[10px]">
                    {correction.strategy.replace("_", " ")}
                  </Badge>
                  <span className="text-muted-foreground">
                    Δ{correction.deltaPercent.toFixed(1)}%
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* System Truth Statement */}
        <div className="border-t pt-3 space-y-2">
          <div className="flex items-center gap-2">
            <Eye className="h-4 w-4 text-primary" />
            <span className="text-sm font-medium">SYSTEM TRUTH</span>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-xs">
            <div className="space-y-1">
              <p className="font-medium text-green-600">✓ Guarantees</p>
              <ul className="text-muted-foreground space-y-0.5">
                {assertion.guarantees.slice(0, 4).map((g, i) => (
                  <li key={i} className="flex items-start gap-1">
                    <CheckCircle2 className="h-3 w-3 mt-0.5 flex-shrink-0 text-green-500" />
                    {g}
                  </li>
                ))}
              </ul>
            </div>
            <div className="space-y-1">
              <p className="font-medium text-yellow-600">⚠ Limitations</p>
              <ul className="text-muted-foreground space-y-0.5">
                {assertion.limitations.slice(0, 4).map((l, i) => (
                  <li key={i} className="flex items-start gap-1">
                    <AlertTriangle className="h-3 w-3 mt-0.5 flex-shrink-0 text-yellow-500" />
                    {l}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

function MetricBox({
  icon,
  label,
  value,
  color,
}: {
  icon: React.ReactNode;
  label: string;
  value: number;
  color: string;
}) {
  return (
    <div className="flex flex-col items-center p-3 bg-muted/30 rounded-lg">
      {icon}
      <span className={`text-xl font-bold ${color}`}>{value}</span>
      <span className="text-[10px] text-muted-foreground text-center">{label}</span>
    </div>
  );
}

function StatBadge({
  label,
  value,
  variant,
}: {
  label: string;
  value: number;
  variant: "default" | "secondary" | "outline" | "destructive";
}) {
  return (
    <div className="flex items-center justify-between p-2 border rounded">
      <span className="text-xs text-muted-foreground">{label}</span>
      <Badge variant={variant} className="text-xs">
        {value}
      </Badge>
    </div>
  );
}
