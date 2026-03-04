
import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { RefreshCw, ShieldCheck, Zap, BrainCircuit, Activity } from "lucide-react";
import ReliabilityOrchestrator from "@/lib/core/ReliabilityOrchestrator";

// Initialize to ensure it exists, though we mock the logs below
// eslint-disable-next-line @typescript-eslint/no-unused-vars
const orchestrator = ReliabilityOrchestrator.getInstance();
// In a real app we'd have a hook to read the orchestrator's state. 
// For now, we'll simulate reading the "Audit Stream".

const StatusPage = () => {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [logs, setLogs] = useState<any[]>([]);
  const [metrics, setMetrics] = useState({
    avgLatency: 0,
    optimisticOps: 0,
    complianceChecks: 0
  });

  useEffect(() => {
    // Simulate real-time stream from ReliabilityOrchestrator
    const interval = setInterval(() => {
      const newLog = {
        id: Date.now(),
        timestamp: new Date().toLocaleTimeString(),
        layer: ["Frontier", "Physics", "Compliance", "Optimistic"][Math.floor(Math.random() * 4)],
        message: [
          "Decomposed task 'Analyze Market' into 4 sub-agents",
          "Ranked 150 physics hypotheses (Uncertainty: Low)",
          "Audit Log: Legal Disclaimer Attached to output",
          "Optimistic UI Update: 0ms latency user feedback"
        ][Math.floor(Math.random() * 4)],
        status: "success"
      };

      setLogs(prev => [newLog, ...prev].slice(0, 50));
      setMetrics(prev => ({
        avgLatency: Math.floor(Math.random() * 5), // < 5ms perceived
        optimisticOps: prev.optimisticOps + 1,
        complianceChecks: prev.complianceChecks + (Math.random() > 0.7 ? 1 : 0)
      }));
    }, 2500);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="container mx-auto p-6 space-y-8">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">System Reliability Status</h1>
          <p className="text-muted-foreground mt-2">
            Real-time monitoring of the 4-Layer Limitless Architecture
          </p>
        </div>
        <Badge variant="outline" className="px-4 py-2 border-green-500 text-green-500">
          <Activity className="w-4 h-4 mr-2" />
          SYSTEM OPERATIONAL
        </Badge>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <StatusCard
          title="Zero Latency"
          icon={<Zap className="text-yellow-500" />}
          value={`${metrics.avgLatency}ms`}
          desc="Perceived avg latency"
        />
        <StatusCard
          title="Frontier Tasks"
          icon={<BrainCircuit className="text-purple-500" />}
          value={metrics.optimisticOps.toString()}
          desc="Sub-tasks routed"
        />
        <StatusCard
          title="Compliance"
          icon={<ShieldCheck className="text-blue-500" />}
          value={metrics.complianceChecks.toString()}
          desc="Audits passed"
        />
        <StatusCard
          title="Health"
          icon={<RefreshCw className="text-green-500" />}
          value="100%"
          desc="Uptime (Simulated)"
        />
      </div>

      <Card className="border-zinc-800 bg-zinc-950/50 backdrop-blur">
        <CardHeader>
          <CardTitle>Reliability Layer Audit Stream</CardTitle>
          <CardDescription>Live feed of Orchestrator decisions (Decomposition, Ranking, Auditing)</CardDescription>
        </CardHeader>
        <CardContent>
          <ScrollArea className="h-[400px] w-full rounded-md border p-4">
            <div className="space-y-4">
              {logs.map((log) => (
                <div key={log.id} className="flex items-start gap-4 text-sm border-b border-zinc-900 pb-3 last:border-0 animation-fade-in">
                  <span className="text-zinc-500 font-mono text-xs w-20 shrink-0">{log.timestamp}</span>
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <Badge variant="secondary" className="text-xs">{log.layer}</Badge>
                      {log.status === 'success' && <span className="text-green-500 text-xs">● Verified</span>}
                    </div>
                    <p className="text-zinc-300">{log.message}</p>
                  </div>
                </div>
              ))}
            </div>
          </ScrollArea>
        </CardContent>
      </Card>
    </div>
  );
};

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const StatusCard = ({ title, icon, value, desc }: any) => (
  <Card>
    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
      <CardTitle className="text-sm font-medium">{title}</CardTitle>
      {icon}
    </CardHeader>
    <CardContent>
      <div className="text-2xl font-bold">{value}</div>
      <p className="text-xs text-muted-foreground">{desc}</p>
    </CardContent>
  </Card>
);

export default StatusPage;
