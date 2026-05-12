import { createExecutionPlan, JobSpec } from './executionAgent';
import { runCpuJob } from '../engines/cpuEngine';
import { runGpuJob } from '../engines/gpuEngine';
import { runTextJob, TextJobPayload } from '../engines/textEngine';
import { runImageJob, ImageJobPayload } from '../engines/imageEngine';
import { runSimulationJob, SimulationJobPayload } from '../engines/simEngine';

export interface AgentJobResult {
  jobId: string;
  engineUsed: 'cpu' | 'gpu' | 'hybrid';
  details: unknown;
}

/**
 * High-level entry point for your app: ask the “agent” to run a demo heavy job.
 * You can import and call this from any React component or other frontend code.
 */
export async function runDemoJobWithAgent(payload: unknown): Promise<AgentJobResult> {
  const job: JobSpec = {
    id: `job-${Date.now()}`,
    kind: 'demo-heavy-compute',
    payload,
  };

  const plan = await createExecutionPlan(job);

  if (plan.engine === 'cpu') {
    const res = await runCpuJob(job.id, payload);
    return {
      jobId: job.id,
      engineUsed: 'cpu',
      details: res,
    };
  }

  if (plan.engine === 'gpu') {
    const res = await runGpuJob(job.id, payload);
    return {
      jobId: job.id,
      engineUsed: 'gpu',
      details: res,
    };
  }

  // Hybrid: run CPU work and try to touch GPU as well.
  const [cpuRes, gpuRes] = await Promise.all([
    runCpuJob(job.id, payload),
    runGpuJob(job.id, payload),
  ]);

  return {
    jobId: job.id,
    engineUsed: 'hybrid',
    details: { cpuRes, gpuRes },
  };
}

export async function runTextJobWithAgent(payload: TextJobPayload): Promise<AgentJobResult> {
  const job: JobSpec = {
    id: `text-${Date.now()}`,
    kind: 'text',
    payload,
  };

  const plan = await createExecutionPlan(job);
  const res = await runTextJob(job.id, payload);

  return {
    jobId: job.id,
    engineUsed: plan.engine,
    details: res,
  };
}

export async function runImageJobWithAgent(payload: ImageJobPayload): Promise<AgentJobResult> {
  const job: JobSpec = {
    id: `image-${Date.now()}`,
    kind: 'image',
    payload,
  };

  const plan = await createExecutionPlan(job);
  const res = await runImageJob(job.id, payload);

  return {
    jobId: job.id,
    engineUsed: plan.engine,
    details: res,
  };
}

export async function runSimulationJobWithAgent(
  payload: SimulationJobPayload
): Promise<AgentJobResult> {
  const job: JobSpec = {
    id: `sim-${Date.now()}`,
    kind: 'simulation',
    payload,
  };

  const plan = await createExecutionPlan(job);
  const res = await runSimulationJob(job.id, payload);

  return {
    jobId: job.id,
    engineUsed: plan.engine,
    details: res,
  };
}


