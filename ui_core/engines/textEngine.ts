import { runCpuJob } from './cpuEngine';

export interface TextJobPayload {
  prompt: string;
}

export interface TextJobResult {
  jobId: string;
  output: string;
  durationMs: number;
  note: string;
}

// Placeholder text engine: today it just echoes the prompt.
// In the future, plug in an efficient local model or retrieval here.
export async function runTextJob(jobId: string, payload: TextJobPayload): Promise<TextJobResult> {
  const cpuRes = await runCpuJob(jobId, payload);

  return {
    jobId,
    output: payload.prompt,
    durationMs: cpuRes.durationMs,
    note: 'Text engine placeholder. Replace with local model or retrieval system.',
  };
}

