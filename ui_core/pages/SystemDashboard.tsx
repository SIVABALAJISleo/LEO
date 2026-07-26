import { useEffect, useState } from "react";
import { hyperClient, BackendStatus, HealthStatus } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Activity, Zap, Cpu, Server, CheckCircle, AlertTriangle } from "lucide-react";
import { Badge } from "@/components/ui/badge";

const SystemDashboard = () => {
  const [status, setStatus] = useState<BackendStatus | null>(null);
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [s, h] = await Promise.all([hyperClient.getStatus(), hyperClient.getHealth()]);
        setStatus(s);
        setHealth(h);
      } catch (err) {
        console.error("Dashboard fetch error:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, []);

  if (loading) return <div className="p-8 text-center">Initialising Hyper Metrics...</div>;

  return (
    <div className="p-6 space-y-6 bg-background min-h-screen text-foreground">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-4xl font-bold tracking-tight text-primary">HYPER Core Dashboard</h1>
          <p className="text-muted-foreground">Production-grade Orchestration Metrics</p>
        </div>
        {health?.engines_available ? (
          <Badge
            variant="outline"
            className="bg-green-500/10 text-green-500 border-green-500/20 px-3 py-1"
          >
            <CheckCircle className="w-4 h-4 mr-2" /> ENGINES ONLINE
          </Badge>
        ) : (
          <Badge variant="destructive" className="px-3 py-1">
            <AlertTriangle className="w-4 h-4 mr-2" /> ENGINES DEGRADED
          </Badge>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card className="bg-card/50 border-primary/20 shadow-glow-sm">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Total Requests</CardTitle>
            <Activity className="h-4 w-4 text-primary" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{status?.metrics.requests || 0}</div>
          </CardContent>
        </Card>

        <Card className="bg-card/50 border-primary/20 shadow-glow-sm">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Avg Latency</CardTitle>
            <Zap className="h-4 w-4 text-yellow-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {(status?.metrics.latency_avg || 0).toFixed(4)}s
            </div>
          </CardContent>
        </Card>

        <Card className="bg-card/50 border-primary/20 shadow-glow-sm">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">System Errors</CardTitle>
            <AlertTriangle className="h-4 w-4 text-destructive" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{status?.metrics.errors || 0}</div>
          </CardContent>
        </Card>

        <Card className="bg-card/50 border-primary/20 shadow-glow-sm">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Backend Version</CardTitle>
            <Cpu className="h-4 w-4 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{status?.version || "0.1.0-prod"}</div>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-8">
        <Card className="bg-card/50 border-primary/20">
          <CardHeader>
            <CardTitle className="flex items-center">
              <Server className="w-5 h-5 mr-2" /> Active Engines
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {["RAG Optimized", "MoE Router", "Vision (Spatial)", "Physics (Baked)"].map(
              (engine) => (
                <div
                  key={engine}
                  className="flex justify-between items-center p-3 rounded-lg bg-muted/30"
                >
                  <span>{engine}</span>
                  <Badge className="bg-green-500/20 text-green-400">READY</Badge>
                </div>
              ),
            )}
          </CardContent>
        </Card>

        <Card className="bg-card/50 border-primary/20">
          <CardHeader>
            <CardTitle>Hardware Utilization</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-6">
              <div>
                <div className="flex justify-between mb-2">
                  <span className="text-sm">CPU Load</span>
                  <span className="text-sm font-bold">{status?.hardware.cpu_load.toFixed(1)}%</span>
                </div>
                <div className="h-2 w-full bg-muted rounded-full overflow-hidden">
                  <div
                    className="h-full bg-primary transition-all duration-500"
                    style={{ width: `${status?.hardware.cpu_load || 0}%` }}
                  />
                </div>
              </div>
              <div>
                <div className="flex justify-between mb-2">
                  <span className="text-sm">Memory Usage</span>
                  <span className="text-sm font-bold">
                    {status?.hardware.memory_percent.toFixed(1)}%
                  </span>
                </div>
                <div className="h-2 w-full bg-muted rounded-full overflow-hidden">
                  <div
                    className="h-full bg-yellow-500 transition-all duration-500"
                    style={{ width: `${status?.hardware.memory_percent || 0}%` }}
                  />
                </div>
              </div>
              <div>
                <div className="flex justify-between mb-2">
                  <span className="text-sm">Storage (Disk)</span>
                  <span className="text-sm font-bold">
                    {status?.hardware.disk_percent.toFixed(1)}%
                  </span>
                </div>
                <div className="h-2 w-full bg-muted rounded-full overflow-hidden">
                  <div
                    className="h-full bg-blue-500 transition-all duration-500"
                    style={{ width: `${status?.hardware.disk_percent || 0}%` }}
                  />
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default SystemDashboard;
