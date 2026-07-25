import { createFileRoute } from "@tanstack/react-router";

// Server-Sent Events stream of the same counters exposed by /metrics.
// Pushes an update every 1s so the frontend benchmark runner can render
// server-side rps/total without polling.

const STARTED_AT = Date.now();
let total = 0;
const last60: number[] = [];

function tick() {
  const now = Date.now();
  total += 1;
  last60.push(now);
  const cutoff = now - 60_000;
  while (last60.length && last60[0] < cutoff) last60.shift();
  return {
    leo_total_requests: total,
    leo_requests_last_60s: last60.length,
    leo_rps_60s: Number((last60.length / 60).toFixed(3)),
    leo_uptime_seconds: Math.floor((now - STARTED_AT) / 1000),
    leo_timestamp: new Date(now).toISOString(),
    leo_source: "tanstack-sse",
  };
}

export const Route = createFileRoute("/api/v1/leo/metrics/stream")({
  server: {
    handlers: {
      GET: async () => {
        const encoder = new TextEncoder();
        const stream = new ReadableStream({
          start(controller) {
            const send = () => {
              const payload = JSON.stringify(tick());
              controller.enqueue(encoder.encode(`event: metrics\ndata: ${payload}\n\n`));
            };
            send();
            const id = setInterval(send, 1000);
            // Auto-close after 10 minutes to avoid runaway streams.
            const stop = setTimeout(() => {
              clearInterval(id);
              try {
                controller.close();
              } catch {
                /* noop */
              }
            }, 10 * 60_000);
            // @ts-expect-error attach cleanup on the controller for cancel().
            controller._cleanup = () => {
              clearInterval(id);
              clearTimeout(stop);
            };
          },
          cancel(reason) {
            // @ts-expect-error see above.
            this._cleanup?.(reason);
          },
        });
        return new Response(stream, {
          headers: {
            "Content-Type": "text/event-stream",
            "Cache-Control": "no-store, no-transform",
            Connection: "keep-alive",
            "Access-Control-Allow-Origin": "*",
          },
        });
      },
    },
  },
});
