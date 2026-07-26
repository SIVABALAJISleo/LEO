import React, { useEffect, useState } from "react";
import { BarChart2, Play, RefreshCw, AlertCircle } from "lucide-react";

export const BenchmarkLeaderboard: React.FC = () => {
  const [results, setResults] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [running, setRunning] = useState(false);

  const fetchResults = async () => {
    try {
      const response = await fetch("http://localhost:8000/api/v1/leo/benchmark/results");
      const data = await response.json();
      setResults(data);
      if (data.status === "running") setRunning(true);
      else setRunning(false);
    } catch (e) {
      console.error("Error fetching benchmark results", e);
    }
  };

  useEffect(() => {
    fetchResults();
    const interval = setInterval(() => {
      if (running) fetchResults();
    }, 2000);
    return () => clearInterval(interval);
  }, [running]);

  const startBenchmark = async () => {
    try {
      setLoading(true);
      await fetch("http://localhost:8000/api/v1/leo/benchmark/run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ num_queries: 10 }),
      });
      setRunning(true);
      setLoading(false);
    } catch (e) {
      console.error("Error starting benchmark", e);
      setLoading(false);
    }
  };

  if (!results) {
    return (
      <div className="bg-[#030d1e] border border-slate-800 rounded-xl p-6 flex justify-center items-center h-64">
        <RefreshCw className="h-8 w-8 animate-spin text-blue-500" />
      </div>
    );
  }

  const models = Object.keys(results.models || {})
    .map((key) => ({
      name: key,
      ...results.models[key],
    }))
    .sort((a, b) => b.accuracy - a.accuracy);

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      <div className="bg-[#030d1e] border border-slate-800 rounded-xl p-6">
        <div className="flex justify-between items-center mb-6">
          <div>
            <h3 className="text-lg font-bold flex items-center gap-2 text-blue-400">
              <BarChart2 className="h-5 w-5" />
              Live Enterprise Benchmark Results
            </h3>
            <p className="text-xs text-slate-400 mt-1">
              Real-time API benchmarking against MSR dataset. Status:{" "}
              <span
                className={`font-bold uppercase ${results.status === "running" ? "text-amber-400" : "text-emerald-400"}`}
              >
                {results.status}
              </span>
            </p>
          </div>
          <button
            onClick={startBenchmark}
            disabled={running || loading}
            className="flex items-center gap-2 bg-blue-600 hover:bg-blue-500 text-white px-4 py-2 rounded-lg text-xs font-bold transition-colors disabled:opacity-50"
          >
            {running ? (
              <RefreshCw className="h-4 w-4 animate-spin" />
            ) : (
              <Play className="h-4 w-4" />
            )}
            {running ? "Running..." : "Start Validation Benchmark"}
          </button>
        </div>

        {results.error && (
          <div className="bg-rose-500/10 border border-rose-500/20 text-rose-400 p-4 rounded-lg text-xs flex items-center gap-2 mb-6">
            <AlertCircle className="h-4 w-4" />
            {results.error}
          </div>
        )}

        <div className="border border-slate-800 rounded-lg overflow-hidden">
          <table className="w-full text-xs text-left">
            <thead className="bg-[#020813] border-b border-slate-800 text-slate-400 uppercase tracking-wider text-[10px]">
              <tr>
                <th className="p-4">Rank</th>
                <th className="p-4">Model Name</th>
                <th className="p-4">Accuracy (Measured)</th>
                <th className="p-4">Avg Latency</th>
                <th className="p-4">Est. Cost</th>
                <th className="p-4">Queries Processed</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800 text-slate-200">
              {models.map((model, index) => (
                <tr key={model.name} className={model.name.includes("LEO") ? "bg-blue-500/5" : ""}>
                  <td
                    className={`p-4 font-bold ${model.name.includes("LEO") ? "text-blue-400" : "text-slate-400"}`}
                  >
                    {index + 1}
                  </td>
                  <td className="p-4 font-bold flex items-center gap-1.5">
                    {model.name.replace(/_/g, " ")}
                    {model.name.includes("LEO") && (
                      <span className="text-[9px] bg-blue-500 text-white px-1.5 py-0.5 rounded font-mono uppercase font-bold">
                        Local-First
                      </span>
                    )}
                  </td>
                  <td
                    className={`p-4 font-bold ${model.accuracy >= 90 ? "text-emerald-400" : model.accuracy >= 50 ? "text-amber-400" : "text-slate-500"}`}
                  >
                    {model.accuracy.toFixed(1)}%
                  </td>
                  <td className="p-4 font-mono text-slate-400">
                    {model.latency_ms > 0 ? `${model.latency_ms.toFixed(1)}ms` : "N/A"}
                  </td>
                  <td className="p-4 font-mono text-rose-400">
                    {model.cost > 0 ? `$${model.cost.toFixed(4)}` : "$0.0000"}
                  </td>
                  <td className="p-4 font-mono text-slate-400">{model.queries_run}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {results.history && results.history.length > 0 && (
          <div className="mt-8 border-t border-slate-800 pt-6">
            <h4 className="text-sm font-bold text-slate-300 mb-4">Latest Queries</h4>
            <div className="space-y-3">
              {results.history
                .slice(-3)
                .reverse()
                .map((h: any, i: number) => (
                  <div
                    key={i}
                    className="bg-[#020813] border border-slate-800 p-4 rounded text-xs text-slate-400"
                  >
                    <p className="text-slate-300 font-semibold mb-2">Q: {h.query}</p>
                    <div className="grid grid-cols-2 gap-2 text-[10px]">
                      <div>
                        LEO: {h.leo.accuracy.toFixed(0)}% ({h.leo.latency.toFixed(0)}ms)
                      </div>
                      <div>
                        GPT: {h.gpt.accuracy.toFixed(0)}% ({h.gpt.latency.toFixed(0)}ms)
                      </div>
                      <div>
                        Claude: {h.claude.accuracy.toFixed(0)}% ({h.claude.latency.toFixed(0)}ms)
                      </div>
                      <div>
                        Gemini: {h.gemini.accuracy.toFixed(0)}% ({h.gemini.latency.toFixed(0)}ms)
                      </div>
                    </div>
                  </div>
                ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
