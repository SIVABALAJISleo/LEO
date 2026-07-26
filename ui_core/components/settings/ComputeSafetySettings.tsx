import {
  Shield,
  Cpu,
  Thermometer,
  Wifi,
  WifiOff,
  Brain,
  Activity,
  CheckCircle,
  AlertTriangle,
  Flame,
  HardDrive,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Separator } from "@/components/ui/separator";
import { useSafeCompute } from "@/hooks/useSafeCompute";
import { cn } from "@/lib/utils";

export const ComputeSafetySettings = () => {
  const {
    systemLoad,
    thermalState,
    isOnline,
    pendingSyncs,
    currentModel,
    getThermalLevel,
    getLoadStatus,
    getRecommendedAction,
    getModelRecommendation,
  } = useSafeCompute();

  const thermalLevel = getThermalLevel();
  const loadStatus = getLoadStatus();
  const action = getRecommendedAction();
  const modelRec = getModelRecommendation();

  const getThermalColor = () => {
    switch (thermalLevel) {
      case "emergency":
        return "text-red-500";
      case "critical":
        return "text-orange-500";
      case "warning":
        return "text-yellow-500";
      default:
        return "text-primary";
    }
  };

  const getThermalIcon = () => {
    switch (thermalLevel) {
      case "emergency":
      case "critical":
        return <Flame className="h-5 w-5 text-red-500" />;
      case "warning":
        return <AlertTriangle className="h-5 w-5 text-yellow-500" />;
      default:
        return <CheckCircle className="h-5 w-5 text-primary" />;
    }
  };

  return (
    <div className="space-y-6">
      {/* Safe-Compute Status */}
      <Card className="bg-card border-border">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Shield className="h-5 w-5 text-primary" />
              <CardTitle>HYPER Safe-Compute Layer</CardTitle>
            </div>
            <Badge className="bg-primary/20 text-primary border-primary/50">Active</Badge>
          </div>
          <CardDescription>
            Secure local compute with automatic protection against crashes, overheating, and network
            failures
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Module Status Grid */}
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            <ModuleStatus
              icon={<Cpu className="h-4 w-4" />}
              name="SafeComputeJobManager"
              status="Active"
              description="Local job execution"
            />
            <ModuleStatus
              icon={<Activity className="h-4 w-4" />}
              name="SmartLoadController"
              status="Active"
              description="Performance optimization"
            />
            <ModuleStatus
              icon={isOnline ? <Wifi className="h-4 w-4" /> : <WifiOff className="h-4 w-4" />}
              name="OfflineJobRunner"
              status={isOnline ? "Online" : "Offline"}
              description={pendingSyncs > 0 ? `${pendingSyncs} pending sync` : "All synced"}
            />
            <ModuleStatus
              icon={<Shield className="h-4 w-4" />}
              name="SecureResultGateway"
              status="Active"
              description="Output sanitization"
            />
            <ModuleStatus
              icon={<Brain className="h-4 w-4" />}
              name="AdaptiveModelSelector"
              status="Active"
              description={currentModel?.name || "Auto-selecting"}
            />
            <ModuleStatus
              icon={<Thermometer className="h-4 w-4" />}
              name="ThermalGuardian"
              status={thermalLevel === "safe" ? "Normal" : thermalLevel}
              description={action.message.slice(0, 30) + "..."}
              warning={thermalLevel !== "safe"}
            />
          </div>
        </CardContent>
      </Card>

      {/* System Resources */}
      <Card className="bg-card border-border">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <HardDrive className="h-5 w-5" />
            System Resources
          </CardTitle>
          <CardDescription>Current system load and performance metrics</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <ResourceBar label="CPU Usage" value={systemLoad.cpuUsage} color="primary" />
          <ResourceBar
            label="Memory Usage"
            value={systemLoad.memoryUsage}
            color={systemLoad.memoryUsage > 80 ? "warning" : "primary"}
          />
          <ResourceBar
            label="GPU Memory"
            value={systemLoad.gpuMemoryUsage}
            color={systemLoad.gpuMemoryUsage > 80 ? "warning" : "primary"}
          />

          <Separator />

          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              {getThermalIcon()}
              <span className="text-sm font-medium">Temperature</span>
            </div>
            <span className={cn("font-mono font-bold", getThermalColor())}>
              {Math.round(thermalState.cpuTemp)}°C CPU / {Math.round(thermalState.gpuTemp)}°C GPU
            </span>
          </div>

          <div className="flex items-center justify-between">
            <span className="text-sm text-muted-foreground">Available RAM</span>
            <span className="font-medium">{Math.round(systemLoad.availableRam)} MB</span>
          </div>

          <div className="flex items-center justify-between">
            <span className="text-sm text-muted-foreground">Load Status</span>
            <Badge
              variant="outline"
              className={cn(
                loadStatus === "critical" && "border-destructive text-destructive",
                loadStatus === "heavy" && "border-orange-500 text-orange-500",
                loadStatus === "moderate" && "border-yellow-500 text-yellow-500",
                (loadStatus === "light" || loadStatus === "idle") && "border-primary text-primary",
              )}
            >
              {loadStatus.charAt(0).toUpperCase() + loadStatus.slice(1)}
            </Badge>
          </div>
        </CardContent>
      </Card>

      {/* Active Model */}
      <Card className="bg-card border-border">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Brain className="h-5 w-5" />
            Adaptive Model Selection
          </CardTitle>
          <CardDescription>
            Automatically selects the optimal model based on available resources
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {currentModel && (
            <div className="p-4 rounded-lg bg-primary/5 border border-primary/20">
              <div className="flex items-center justify-between mb-2">
                <span className="font-semibold text-primary">{currentModel.name}</span>
                <Badge>{currentModel.size.toUpperCase()}</Badge>
              </div>
              <div className="grid grid-cols-3 gap-4 text-sm">
                <div>
                  <span className="text-muted-foreground">RAM Required</span>
                  <p className="font-medium">{currentModel.requiredRamMb} MB</p>
                </div>
                <div>
                  <span className="text-muted-foreground">Accuracy</span>
                  <p className="font-medium">{Math.round(currentModel.accuracy * 100)}%</p>
                </div>
                <div>
                  <span className="text-muted-foreground">Speed</span>
                  <p className="font-medium">{Math.round(currentModel.speed * 100)}%</p>
                </div>
              </div>
            </div>
          )}

          <div className="p-3 rounded-md bg-muted/50">
            <p className="text-sm text-muted-foreground">{modelRec.reason}</p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

const ModuleStatus = ({
  icon,
  name,
  status,
  description,
  warning = false,
}: {
  icon: React.ReactNode;
  name: string;
  status: string;
  description: string;
  warning?: boolean;
}) => (
  <div className="p-3 rounded-lg bg-muted/50 border border-border">
    <div className="flex items-center gap-2 mb-1">
      <span className={warning ? "text-yellow-500" : "text-primary"}>{icon}</span>
      <span className="text-xs font-medium truncate">{name}</span>
    </div>
    <div className="flex items-center justify-between">
      <Badge
        variant="outline"
        className={cn(
          "text-xs",
          warning ? "border-yellow-500/50 text-yellow-500" : "border-primary/50 text-primary",
        )}
      >
        {status}
      </Badge>
    </div>
    <p className="text-xs text-muted-foreground mt-1 truncate">{description}</p>
  </div>
);

const ResourceBar = ({
  label,
  value,
  color,
}: {
  label: string;
  value: number;
  color: "primary" | "warning";
}) => (
  <div className="space-y-1">
    <div className="flex items-center justify-between text-sm">
      <span className="text-muted-foreground">{label}</span>
      <span className="font-medium">{Math.round(value)}%</span>
    </div>
    <Progress value={value} className={cn("h-2", color === "warning" && "[&>div]:bg-yellow-500")} />
  </div>
);
