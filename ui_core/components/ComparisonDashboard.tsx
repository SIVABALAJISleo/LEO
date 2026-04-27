import React, { useState } from 'react';
import useAgentDemoJob from '../hooks/useAgentDemo';
import { calculateEfficiency, EfficiencyResult } from '../benchmarking';

export function ComparisonDashboard() {
  const { running, lastResult, error, run } = useAgentDemoJob();
  const [eff, setEff] = useState<EfficiencyResult | null>(null);

  const handleRun = async () => {
    const start = performance.now();
    await run();
    const localLatency = performance.now() - start;
    const result = calculateEfficiency(localLatency);
    setEff(result);
  };

  return (
    <div style={{ padding: '1rem', border: '1px solid #444', borderRadius: 8 }}>
      <h2>Local vs Simulated Cloud Comparison</h2>
      <button onClick={handleRun} disabled={running} style={{ padding: '0.5rem 1rem' }}>
        {running ? 'Running local job…' : 'Run Local Job'}
      </button>

      {error && <p style={{ color: 'red' }}>Error: {error}</p>}

      {lastResult && (
        <div style={{ marginTop: '1rem' }}>
          <h3>Last Agent Job</h3>
          <pre style={{ maxHeight: 200, overflow: 'auto', background: '#111', color: '#eee' }}>
            {JSON.stringify(lastResult, null, 2)}
          </pre>
        </div>
      )}

      {eff && (
        <div style={{ marginTop: '1rem' }}>
          <h3>Benchmark Metrics</h3>
          <p>
            <strong>Local Latency:</strong> {eff.localLatencyMs.toFixed(1)} ms
          </p>
          <p>
            <strong>Simulated Cloud Latency:</strong> {eff.simulatedCloudLatencyMs.toFixed(1)} ms
          </p>
          <p>
            <strong>Local Cost:</strong> ${eff.localCostUsd.toFixed(2)} per job
          </p>
          <p>
            <strong>Simulated Cloud Cost:</strong> ${eff.simulatedCloudCostUsd.toFixed(2)} per job
          </p>
          <p>
            <strong>Efficiency Ratio:</strong> {eff.efficiencyRating.toFixed(1)}%
          </p>
          <p>
            <strong>Bypass Success:</strong> {eff.bypassSuccess ? 'Yes (local is faster or equal)' : 'No'}
          </p>
        </div>
      )}
    </div>
  );
}

export default ComparisonDashboard;

