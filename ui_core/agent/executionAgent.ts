// High‑level “agentic” orchestrator for choosing how to run heavy jobs locally.
// This does NOT break hardware limits; it simply uses the device as efficiently as possible.

export type EngineType = 'cpu' | 'gpu' | 'hybrid';

export interface DeviceProfile {
  hasWebGPU: boolean;
  logicalCores: number;
  userAgent: string;
}

export type JobKind = 'demo-heavy-compute' | 'text' | 'image' | 'simulation';

export interface JobSpec {
  id: string;
  kind: JobKind;
  payload: unknown;
}

export interface ExecutionPlan {
  engine: EngineType;
  profile: DeviceProfile;
}

export async function detectDeviceProfile(): Promise<DeviceProfile> {
  if (typeof navigator === 'undefined') {
    // Server-side / non-browser environment
    return {
      hasWebGPU: false,
      logicalCores: 1,
      userAgent: 'server',
    };
  }

  const hasWebGPU = typeof (navigator as any).gpu !== 'undefined';
  const logicalCores = typeof navigator.hardwareConcurrency === 'number'
    ? navigator.hardwareConcurrency
    : 2;

  return {
    hasWebGPU,
    logicalCores,
    userAgent: navigator.userAgent,
  };
}

/**
 * Simple rule‑based “agent” that decides which engine to use.
 * This can later be replaced or enhanced by an AI model if you want.
 */
export async function createExecutionPlan(job: JobSpec): Promise<ExecutionPlan> {
  const profile = await detectDeviceProfile();

  // Very simple strategy for now:
  // - If WebGPU is available and we have at least 4 logical cores, prefer a hybrid plan.
  // - If WebGPU is available but few cores, prefer GPU.
  // - Otherwise, CPU only.
  if (profile.hasWebGPU && profile.logicalCores >= 4) {
    return { engine: 'hybrid', profile };
  }

  if (profile.hasWebGPU) {
    return { engine: 'gpu', profile };
  }

  return { engine: 'cpu', profile };
}

