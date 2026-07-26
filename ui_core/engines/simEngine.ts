import { runCpuJob } from "./cpuEngine";
import { runGpuJob } from "./gpuEngine";

export interface SimulationJobPayload {
  steps?: number;
}

export interface SimulationJobResult {
  jobId: string;
  cpuDurationMs: number;
  gpuNote: string;
  note: string;
}

// Placeholder simulation engine: today it simply uses the demo CPU job and,
// if available, a no-op GPU touch. Later you can implement SDF-based or
// event-driven simulations here.
export async function runSimulationJob(
  jobId: string,
  payload: SimulationJobPayload,
): Promise<SimulationJobResult> {
  const [cpuRes, gpuRes] = await Promise.all([
    runCpuJob(jobId, payload),
    runGpuJob(jobId, payload),
  ]);

  return {
    jobId,
    cpuDurationMs: cpuRes.durationMs,
    gpuNote: gpuRes.note,
    note: "Simulation engine placeholder. Replace with efficient SDF/event-driven logic.",
  };
}
