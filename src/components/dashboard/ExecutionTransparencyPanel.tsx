import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { 
  Shield, Cpu, Brain, RefreshCw, ArrowRight, 
  AlertTriangle, CheckCircle2, Zap 
} from "lucide-react";
import { realityMinimizationEngine } from "@/lib/safeCompute";


export function ExecutionTransparencyPanel({ className }: { className?: string }) {
  const stats = realityMinimizationEngine.getStats();
  const assertion = realityMinimizationEngine.getSystemAssertion();

  return (
    <Card className={className}>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg flex items-center gap-2">
            <Shield className="h-5 w-5 text-primary" />
            Reality Minimization Status
          </CardTitle>
          <Badge variant="outline" className="bg-green-500/10 text-green-600">
            {stats.coveragePercent.toFixed(1)}% Coverage
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Path Distribution */}
        <div className="grid grid-cols-3 gap-2 text-sm">
          <div className="flex items-center gap-1">
            <CheckCircle2 className="h-3 w-3 text-green-500" />
            <span className="text-muted-foreground">Inferred:</span>
            <span className="font-medium">{stats.tasksInferred}</span>
          </div>
          <div className="flex items-center gap-1">
            <RefreshCw className="h-3 w-3 text-blue-500" />
            <span className="text-muted-foreground">Reused:</span>
            <span className="font-medium">{stats.tasksReused}</span>
          </div>
          <div className="flex items-center gap-1">
            <Brain className="h-3 w-3 text-purple-500" />
            <span className="text-muted-foreground">Predicted:</span>
            <span className="font-medium">{stats.tasksPredicted}</span>
          </div>
        </div>

        {/* GPU Avoided */}
        <div className="space-y-1">
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">GPU Compute Avoided</span>
            <span className="font-medium">{stats.gpuComputeAvoided} tasks</span>
          </div>
          <Progress 
            value={stats.totalTasks > 0 ? (stats.gpuComputeAvoided / stats.totalTasks) * 100 : 0} 
            className="h-2"
          />
        </div>

        {/* Authority Locked */}
        <div className="flex items-center justify-between p-2 bg-muted/50 rounded-lg">
          <div className="flex items-center gap-2">
            <AlertTriangle className="h-4 w-4 text-yellow-500" />
            <span className="text-sm">Authority-Locked Tasks</span>
          </div>
          <Badge variant="secondary">{stats.authorityLockedPercent.toFixed(1)}%</Badge>
        </div>

        {/* System Truth */}
        <div className="text-xs text-muted-foreground border-t pt-3 space-y-1">
          <p className="font-medium text-foreground">{assertion.statement}</p>
          <ul className="list-disc list-inside space-y-0.5">
            {assertion.limitations.slice(0, 3).map((lim, i) => (
              <li key={i}>{lim}</li>
            ))}
          </ul>
        </div>
      </CardContent>
    </Card>
  );
}
