import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  ArrowRight,
  Server,
  Cloud,
  Cpu,
  AlertCircle,
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  CheckCircle2,
  Clock,
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  Zap,
} from "lucide-react";
import { workloadClassifier, WorkloadClassification } from "@/lib/safeCompute/WorkloadClassifier";

export type ExecutionDecision = "local" | "defer" | "delegate" | "upgrade_required";

export interface DecisionResult {
  decision: ExecutionDecision;
  reason: string;
  classification?: WorkloadClassification;
  recommendation?: string;
}

interface ExecutionDecisionPanelProps {
  workloadId: string;
  workloadType: string;
  input: unknown;
  onDecision?: (result: DecisionResult) => void;
  className?: string;
}

export const ExecutionDecisionPanel = ({
  workloadId,
  workloadType,
  input,
  onDecision,
  className,
}: ExecutionDecisionPanelProps) => {
  const [decision, setDecision] = useState<DecisionResult | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Classify workload and determine execution path
    const classify = async () => {
      setLoading(true);

      const classification = workloadClassifier.classify(workloadId, workloadType, input, {
        allowDownscale: true,
        userPriority: "cost",
      });

      let result: DecisionResult;

      // Decision logic based on classification
      if (!classification.gpuRequired) {
        result = {
          decision: "local",
          reason: "Workload can be handled without GPU compute",
          classification,
          recommendation: "Execute locally for fastest response",
        };
      } else if (classification.categories.includes("deferrable")) {
        result = {
          decision: "defer",
          reason: "GPU required but workload can wait for optimal window",
          classification,
          recommendation: "Schedule for off-peak execution to reduce costs",
        };
      } else if (classification.delegatable) {
        result = {
          decision: "delegate",
          reason: "GPU required, delegating to available compute resource",
          classification,
          recommendation: "Connect external GPU or use cloud compute",
        };
      } else {
        result = {
          decision: "upgrade_required",
          reason: "Workload requires dedicated GPU that is not available",
          classification,
          recommendation: "Register a GPU device or connect cloud compute",
        };
      }

      setDecision(result);
      setLoading(false);
      onDecision?.(result);
    };

    classify();
  }, [workloadId, workloadType, input, onDecision]);

  if (loading) {
    return (
      <Card className={className}>
        <CardContent className="pt-6">
          <div className="flex items-center gap-2 text-muted-foreground">
            <Cpu className="h-4 w-4 animate-pulse" />
            Analyzing workload...
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!decision) return null;

  const decisionConfig = {
    local: {
      icon: Cpu,
      color: "text-green-500",
      bgColor: "bg-green-500/10",
      badge: "Local",
      badgeVariant: "default" as const,
    },
    defer: {
      icon: Clock,
      color: "text-blue-500",
      bgColor: "bg-blue-500/10",
      badge: "Deferred",
      badgeVariant: "secondary" as const,
    },
    delegate: {
      icon: Cloud,
      color: "text-purple-500",
      bgColor: "bg-purple-500/10",
      badge: "Delegated",
      badgeVariant: "outline" as const,
    },
    upgrade_required: {
      icon: AlertCircle,
      color: "text-yellow-500",
      bgColor: "bg-yellow-500/10",
      badge: "GPU Required",
      badgeVariant: "destructive" as const,
    },
  };

  const config = decisionConfig[decision.decision];
  const IconComponent = config.icon;

  return (
    <Card className={className}>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-sm font-medium">Execution Decision</CardTitle>
          <Badge variant={config.badgeVariant}>{config.badge}</Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        <div className={`flex items-center gap-3 p-3 rounded-lg ${config.bgColor}`}>
          <IconComponent className={`h-6 w-6 ${config.color}`} />
          <div className="flex-1">
            <div className="font-medium">{decision.reason}</div>
            <div className="text-sm text-muted-foreground">{decision.recommendation}</div>
          </div>
        </div>

        {decision.classification && (
          <div className="text-xs space-y-1">
            <div className="flex justify-between">
              <span className="text-muted-foreground">Primary Category</span>
              <span className="font-medium">
                {decision.classification.primaryCategory.replace("_", " ")}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">GPU Required</span>
              <span className="font-medium">
                {decision.classification.gpuRequired ? "Yes" : "No"}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Quality Floor</span>
              <span className="font-medium">
                {Math.round(decision.classification.qualityFloor * 100)}%
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Latency Budget</span>
              <span className="font-medium">{decision.classification.latencyBudgetMs}ms</span>
            </div>
          </div>
        )}

        {decision.decision === "upgrade_required" && (
          <div className="pt-2">
            <Button size="sm" className="w-full">
              <Server className="h-4 w-4 mr-2" />
              Register GPU Device
              <ArrowRight className="h-4 w-4 ml-2" />
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

/**
 * Execution path summary for quick display
 */
interface ExecutionPathBadgeProps {
  decision: ExecutionDecision;
  className?: string;
}

export const ExecutionPathBadge = ({ decision, className }: ExecutionPathBadgeProps) => {
  const configs = {
    local: { icon: Cpu, label: "Local", variant: "default" as const },
    defer: { icon: Clock, label: "Deferred", variant: "secondary" as const },
    delegate: { icon: Cloud, label: "External", variant: "outline" as const },
    upgrade_required: { icon: AlertCircle, label: "GPU Needed", variant: "destructive" as const },
  };

  const config = configs[decision];
  const Icon = config.icon;

  return (
    <Badge variant={config.variant} className={className}>
      <Icon className="h-3 w-3 mr-1" />
      {config.label}
    </Badge>
  );
};

export default ExecutionDecisionPanel;
