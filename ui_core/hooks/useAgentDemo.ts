import { useState, useCallback } from "react";
import { runDemoJobWithAgent, AgentJobResult } from "../agent";

interface AgentDemoState {
  running: boolean;
  lastResult: AgentJobResult | null;
  error: string | null;
}

/**
 * React hook that lets any component trigger the local “agentic” demo job.
 * This stays software-only: it just uses CPU/WebGPU according to the agent plan.
 */
export function useAgentDemoJob(): AgentDemoState & { run: (payload?: unknown) => Promise<void> } {
  const [state, setState] = useState<AgentDemoState>({
    running: false,
    lastResult: null,
    error: null,
  });

  const run = useCallback(async (payload?: unknown) => {
    setState((prev) => ({ ...prev, running: true, error: null }));
    try {
      const res = await runDemoJobWithAgent(payload ?? null);
      setState({ running: false, lastResult: res, error: null });
    } catch (err) {
      setState({
        running: false,
        lastResult: null,
        error: err instanceof Error ? err.message : "Unknown error",
      });
    }
  }, []);

  return { ...state, run };
}

export default useAgentDemoJob;
