// Simple Web Worker that simulates a CPU-heavy task.
// In the future, this can be replaced with real math, ML inference, etc.

interface IncomingMessage {
  type: 'run-demo';
  payload: unknown;
}

interface DoneMessage {
  type: 'done';
  durationMs: number;
}

self.onmessage = (event: MessageEvent<IncomingMessage>) => {
  if (!event.data || event.data.type !== 'run-demo') return;

  const start = performance.now();

  // Simulated heavy numeric work – pure software, CPU only.
  let acc = 0;
  for (let i = 0; i < 20_000_000; i++) {
    acc += Math.sin(i) * Math.cos(i / 2);
  }

  const durationMs = performance.now() - start;

  const msg: DoneMessage = {
    type: 'done',
    durationMs,
  };

  // eslint-disable-next-line no-restricted-globals
  (self as unknown as Worker).postMessage(msg);
};

