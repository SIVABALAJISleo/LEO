// CPU “engine” that runs heavy jobs using Web Workers when available.
// This is a software-only path that tries to use multiple CPU cores safely.

export interface CpuJobResult {
  jobId: string;
  durationMs: number;
  payloadEcho: unknown;
}

interface WorkerMessage {
  type: "done";
  durationMs: number;
}

export async function runCpuJob(jobId: string, payload: unknown): Promise<CpuJobResult> {
  // If we are not in a browser (e.g. during SSR), fall back to a simple sync path.
  if (typeof window === "undefined" || typeof Worker === "undefined") {
    const start = performance.now();
    // Simple simulated heavy work
    for (let i = 0; i < 5_000_000; i++) {
      Math.sqrt(i);
    }
    const durationMs = performance.now() - start;
    return { jobId, durationMs, payloadEcho: payload };
  }

  return new Promise<CpuJobResult>((resolve, reject) => {
    try {
      const worker = new Worker(new URL("../workers/cpuWorker.ts", import.meta.url), {
        type: "module",
      });

      const start = performance.now();

      worker.onmessage = (event: MessageEvent<WorkerMessage>) => {
        if (event.data?.type === "done") {
          const durationMs = performance.now() - start;
          worker.terminate();
          resolve({
            jobId,
            durationMs,
            payloadEcho: payload,
          });
        }
      };

      worker.onerror = (err) => {
        worker.terminate();
        reject(err);
      };

      worker.postMessage({ type: "run-demo", payload });
    } catch (err) {
      reject(err);
    }
  });
}
