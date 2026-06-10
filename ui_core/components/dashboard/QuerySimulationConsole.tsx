import React, { useState } from "react";
import { simulateQuery, OrchestrateResponse } from "../../lib/api";
import { LayerWaterfallChart } from "./LayerWaterfallChart";
import { Loader2, Play, Zap, Server, Database, Cpu } from "lucide-react";

export const QuerySimulationConsole = () => {
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState<OrchestrateResponse | null>(null);
  const [error, setError] = useState("");

  const handleSimulate = async () => {
    if (!query.trim()) return;
    setLoading(true);
    setError("");
    setResponse(null);
    try {
      const res = await simulateQuery({
        query,
        workspace_id: "test-dashboard",
      });
      setResponse(res);
    } catch (err: any) {
      setError(err.message || "Failed to execute query against LEO runtime.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Input Panel */}
      <div className="bg-card border rounded-xl shadow-sm p-6 flex flex-col h-full">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Play className="h-5 w-5 text-blue-500" />
          Execution Simulation Console
        </h3>
        <p className="text-sm text-muted-foreground mb-4">
          Test the runtime intelligence router. Type a query to see how the system avoids GPU usage by routing through the 12-layer OS.
        </p>
        
        <textarea
          className="flex-grow w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring min-h-[120px] mb-4"
          placeholder="e.g. How do I request PTO in the enterprise portal?"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        
        <button
          onClick={handleSimulate}
          disabled={loading || !query.trim()}
          className="w-full bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-4 py-2 rounded-md font-medium transition-colors flex items-center justify-center gap-2 disabled:opacity-50"
        >
          {loading && <Loader2 className="h-4 w-4 animate-spin" />}
          Execute Inference
        </button>

        {error && (
          <div className="mt-4 p-3 bg-destructive/10 text-destructive rounded-md text-sm">
            {error}
          </div>
        )}

        {response && (
          <div className="mt-6 border-t pt-4">
            <h4 className="font-medium text-sm text-muted-foreground mb-2">Final Synthesized Output</h4>
            <div className="bg-muted p-4 rounded-md text-sm font-mono whitespace-pre-wrap text-foreground">
              {response.result}
            </div>
            
            <div className="mt-4 grid grid-cols-2 gap-4">
              <div className="bg-green-500/10 border border-green-500/20 p-3 rounded-md">
                <p className="text-xs font-semibold text-green-600 dark:text-green-400 uppercase tracking-wider mb-1">Resolved By</p>
                <p className="font-mono text-sm">{response.resolved_by}</p>
              </div>
              <div className="bg-blue-500/10 border border-blue-500/20 p-3 rounded-md">
                <p className="text-xs font-semibold text-blue-600 dark:text-blue-400 uppercase tracking-wider mb-1">Compute Avoided</p>
                <p className="font-mono text-sm">{response.compute_avoided ? "Yes (Zero Cloud GPU)" : "No"}</p>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Waterfall Panel */}
      <div className="bg-card border rounded-xl shadow-sm p-6 flex flex-col h-full">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Zap className="h-5 w-5 text-amber-500" />
          Inference Waterfall Trace
        </h3>
        <p className="text-sm text-muted-foreground mb-6">
          Visualizing latency and execution path across the semantic intelligence fabric.
        </p>
        <div className="flex-grow flex flex-col justify-center">
          <LayerWaterfallChart data={response?.layer_trace || []} />
        </div>
      </div>
    </div>
  );
};
