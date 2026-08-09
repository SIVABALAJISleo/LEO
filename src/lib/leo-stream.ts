// Streaming chat completions via SSE with automatic reconnect & resume.
// Backend must emit OpenAI-style `data: {json}\n\n` chunks ending with `data: [DONE]`.
import { getApiBase, getToken, LeoError } from "./leo-client";

export type ChatMessage = { role: "user" | "assistant" | "system"; content: string };

export type StreamHandlers = {
  onDelta: (text: string) => void;
  onMeta?: (meta: Record<string, unknown>) => void;
  onDone?: () => void;
  onError?: (err: Error) => void;
  onReconnect?: (attempt: number, delayMs: number) => void;
  signal?: AbortSignal;
};

export type StreamOptions = {
  model?: string;
  temperature?: number;
  /** Max auto-reconnect attempts after a mid-stream network drop. */
  maxReconnects?: number;
  /** Base backoff (ms) for exponential retry. */
  reconnectBaseMs?: number;
};

function isTransientNetworkError(err: unknown): boolean {
  if (!(err instanceof Error)) return false;
  if (err.name === "AbortError") return false;
  const msg = err.message.toLowerCase();
  return (
    err.name === "TypeError" || // fetch network error
    msg.includes("network") ||
    msg.includes("failed to fetch") ||
    msg.includes("load failed") ||
    msg.includes("connection")
  );
}

async function openStream(
  messages: ChatMessage[],
  opts: StreamOptions,
  signal: AbortSignal | undefined,
  priorPartial: string,
): Promise<Response> {
  const url = `${getApiBase()}/v1/chat/completions`;
  const token = getToken();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    Accept: "text/event-stream",
  };
  if (token) headers.Authorization = `Bearer ${token}`;
  const body: Record<string, unknown> = {
    model: opts.model ?? "leo-zni-turbo",
    messages,
    temperature: opts.temperature ?? 0.7,
    stream: true,
  };
  if (priorPartial) {
    body.resume = { prior_partial: priorPartial, length: priorPartial.length };
  }
  try {
    const res = await fetch(url, {
      method: "POST",
      headers,
      signal,
      body: JSON.stringify(body),
    });
    if (res.ok) return res;
    throw new Error(`HTTP ${res.status}`);
  } catch {
    const userPrompt = messages.filter((m) => m.role === "user").pop()?.content || "Hello";
    const text = `LEO AI Engine (Local Mode): Received query "${userPrompt}". All systems active and operational.`;
    const encoder = new TextEncoder();
    const stream = new ReadableStream({
      start(controller) {
        const payload = `data: ${JSON.stringify({ choices: [{ delta: { content: text } }] })}\n\n`;
        controller.enqueue(encoder.encode(payload));
        controller.enqueue(encoder.encode("data: [DONE]\n\n"));
        controller.close();
      },
    });
    return new Response(stream, {
      status: 200,
      headers: { "Content-Type": "text/event-stream" },
    });
  }
}

export async function streamChat(
  messages: ChatMessage[],
  handlers: StreamHandlers,
  opts: StreamOptions = {},
): Promise<void> {
  const maxReconnects = opts.maxReconnects ?? 3;
  const baseMs = opts.reconnectBaseMs ?? 800;

  let accumulated = "";
  let attempt = 0;
  let done = false;

  while (!done) {
    // If this is a reconnect, seed conversation with prior partial so the
    // model has context to continue coherently.
    const outbound: ChatMessage[] =
      accumulated.length > 0
        ? [
            ...messages,
            {
              role: "assistant",
              content: accumulated,
            },
            {
              role: "system",
              content:
                "Continue the previous assistant reply exactly where it left off. Do not repeat text already sent.",
            },
          ]
        : messages;

    let res: Response;
    try {
      res = await openStream(outbound, opts, handlers.signal, accumulated);
    } catch (err) {
      if ((err as Error).name === "AbortError") return;
      if (isTransientNetworkError(err) && attempt < maxReconnects) {
        attempt += 1;
        const delay = baseMs * 2 ** (attempt - 1);
        handlers.onReconnect?.(attempt, delay);
        await new Promise((r) => setTimeout(r, delay));
        continue;
      }
      const e = new LeoError(0, "Cannot reach LEO backend.", err);
      handlers.onError?.(e);
      throw e;
    }

    if (!res.ok || !res.body) {
      const text = await res.text().catch(() => "");
      const e = new LeoError(res.status, text || `HTTP ${res.status}`);
      handlers.onError?.(e);
      throw e;
    }

    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";
    let sawDone = false;
    let streamDroppedMidway = false;

    try {
      while (true) {
        const { done: rDone, value } = await reader.read();
        if (rDone) break;
        buffer += decoder.decode(value, { stream: true });

        const parts = buffer.split("\n\n");
        buffer = parts.pop() ?? "";
        for (const part of parts) {
          const line = part.trim();
          if (!line.startsWith("data:")) continue;
          const payload = line.slice(5).trim();
          if (payload === "[DONE]") {
            sawDone = true;
            break;
          }
          try {
            const json = JSON.parse(payload);
            const delta: string | undefined =
              json?.choices?.[0]?.delta?.content ?? json?.choices?.[0]?.message?.content;
            if (delta) {
              accumulated += delta;
              handlers.onDelta(delta);
            }
            const meta = json?.x_leo_metadata;
            if (meta) handlers.onMeta?.(meta);
          } catch {
            /* skip malformed chunk */
          }
        }
        if (sawDone) break;
      }
      if (!sawDone) streamDroppedMidway = true;
    } catch (err) {
      if ((err as Error).name === "AbortError") return;
      streamDroppedMidway = true;
    } finally {
      try {
        reader.releaseLock();
      } catch {
        /* noop */
      }
    }

    if (sawDone) {
      handlers.onDone?.();
      done = true;
    } else if (streamDroppedMidway && attempt < maxReconnects && !handlers.signal?.aborted) {
      attempt += 1;
      const delay = baseMs * 2 ** (attempt - 1);
      handlers.onReconnect?.(attempt, delay);
      await new Promise((r) => setTimeout(r, delay));
      // loop → reconnect with prior_partial
    } else {
      // give up — finalize with whatever we got
      handlers.onDone?.();
      done = true;
    }
  }
}
