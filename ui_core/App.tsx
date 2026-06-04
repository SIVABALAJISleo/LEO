import React, { useEffect, useState } from "react";
import { fetchLeoStatus, LeoStatus } from "./lib/api";
import { QuerySimulationConsole } from "./components/Dashboard/QuerySimulationConsole";
import { Activity, Cpu, HardDrive, Layers, Zap, AlertTriangle } from "lucide-react";
import "./index.css";

function App() {
  const [status, setStatus] = useState<LeoStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const loadStatus = async () => {
      try {
        const data = await fetchLeoStatus();
        setStatus(data);
        setError("");
      } catch (err: any) {
        console.error("Failed to fetch backend status:", err);
        setError("Failed to connect to LEO Backend on port 8005. Is it running?");
      } finally {
        setLoading(false);
      }
    };

    loadStatus();
    // Poll every 5 seconds
    const interval = setInterval(loadStatus, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen bg-background text-foreground flex flex-col font-sans">
      {/* Navbar */}
      <header className="border-b sticky top-0 bg-background/95 backdrop-blur z-50">
        <div className="container mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="bg-primary p-1.5 rounded-md">
              <Zap className="h-5 w-5 text-primary-foreground" />
            </div>
            <h1 className="text-xl font-bold tracking-tight">UCSIP <span className="text-muted-foreground font-normal text-sm ml-2">Universal Crystal Swarm Intelligence Platform</span></h1>
          </div>
          <div className="flex items-center gap-4">
            {error ? (
              <span className="flex items-center gap-1.5 text-sm text-destructive font-medium">
                <AlertTriangle className="h-4 w-4" />
                Backend Offline
              </span>
            ) : status ? (
              <span className="flex items-center gap-1.5 text-sm text-green-500 font-medium">
                <span className="relative flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
                </span>
                {status.system} Active
              </span>
            ) : null}
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 container mx-auto px-4 py-8">
        {loading && !status && !error ? (
          <div className="h-64 flex items-center justify-center">
            <Activity className="h-8 w-8 animate-spin text-muted-foreground" />
          </div>
        ) : (
          <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
            
            {/* Top Level Metric Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="bg-card border rounded-xl p-5 shadow-sm">
                <div className="flex items-center gap-2 text-muted-foreground mb-3">
                  <Activity className="h-4 w-4" />
                  <h3 className="text-sm font-medium">Novelty Reduction</h3>
                </div>
                <div className="text-3xl font-bold tracking-tight text-primary">
                  {status?.telemetry?.avoidance_rate_pct?.toFixed(1) || "0.0"}%
                </div>
                <p className="text-xs text-muted-foreground mt-1">Novelty eliminated via Swarm Pipeline</p>
              </div>

              <div className="bg-card border rounded-xl p-5 shadow-sm">
                <div className="flex items-center gap-2 text-muted-foreground mb-3">
                  <Zap className="h-4 w-4 text-green-500" />
                  <h3 className="text-sm font-medium">GPU Energy Saved</h3>
                </div>
                <div className="text-3xl font-bold tracking-tight text-green-500">
                  {((status?.telemetry?.gpu_watts_saved || 0) / 1000).toFixed(1)} kW
                </div>
                <p className="text-xs text-muted-foreground mt-1">NVIDIA GPU irrelevance</p>
              </div>

              <div className="bg-card border rounded-xl p-5 shadow-sm">
                <div className="flex items-center gap-2 text-muted-foreground mb-3">
                  <HardDrive className="h-4 w-4" />
                  <h3 className="text-sm font-medium">Predictive Pre-resolutions</h3>
                </div>
                <div className="text-3xl font-bold tracking-tight">
                  {status?.semantic_store_size?.toLocaleString() || 0}
                </div>
                <p className="text-xs text-muted-foreground mt-1">Precomputed future states</p>
              </div>

              <div className="bg-card border rounded-xl p-5 shadow-sm">
                <div className="flex items-center gap-2 text-muted-foreground mb-3">
                  <Layers className="h-4 w-4" />
                  <h3 className="text-sm font-medium">Discovery Crystals</h3>
                </div>
                <div className="text-3xl font-bold tracking-tight">
                  {status?.fingerprint_store_size?.toLocaleString() || 0}
                </div>
                <p className="text-xs text-muted-foreground mt-1">Scientific Knowledge Crystals</p>
              </div>
            </div>

            {/* Interactive Simulation Console */}
            <section className="pt-4">
              <h2 className="text-xl font-bold mb-4">Runtime Simulation</h2>
              <QuerySimulationConsole />
            </section>

          </div>
        )}
      </main>
    </div>
  );
}

export default App;