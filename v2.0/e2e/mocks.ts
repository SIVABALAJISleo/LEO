import { test, expect, type Route } from "@playwright/test";

/**
 * Mocks the LEO backend so E2E tests are hermetic — no live Python server needed.
 * Intercepts `**\/v1/**` and `**\/api/v1/**` calls and returns canned JSON / SSE.
 */
export async function mockLeoBackend(page: import("@playwright/test").Page) {
  await page.route("**/v1/auth/login", async (route: Route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        access_token: "test-jwt-token-abcdef",
        token_type: "bearer",
        user: { id: "u_1", email: "test@leo.ai" },
      }),
    });
  });

  await page.route("**/v1/auth/signup", async (route: Route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        access_token: "test-jwt-token-abcdef",
        user: { id: "u_1", email: "test@leo.ai" },
      }),
    });
  });

  await page.route("**/api/v1/leo/metrics", async (route: Route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        leo_avoidance_rate_pct: 99.3,
        leo_gpu_watts_saved: 490_000,
        leo_requests_total: 12345,
      }),
    });
  });

  await page.route("**/api/v1/memory**", async (route: Route) => {
    if (route.request().method() === "GET") {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ items: [{ content: "hello world" }] }),
      });
    } else {
      await route.fulfill({ status: 200, contentType: "application/json", body: "{}" });
    }
  });

  await page.route("**/v1/chat/completions", async (route: Route) => {
    const req = route.request();
    const body = req.postDataJSON?.() ?? {};
    if (body?.stream) {
      const sse = [
        `data: ${JSON.stringify({ choices: [{ delta: { content: "Hello " } }] })}`,
        `data: ${JSON.stringify({ choices: [{ delta: { content: "from LEO." } }], x_leo_metadata: { resolved_by: "cache", latency_ms: 8, compute_avoided: true } })}`,
        `data: [DONE]`,
        "",
      ].join("\n\n");
      await route.fulfill({
        status: 200,
        headers: { "content-type": "text/event-stream", "cache-control": "no-cache" },
        body: sse,
      });
    } else {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          choices: [{ message: { role: "assistant", content: "Hello from LEO." } }],
          x_leo_metadata: { resolved_by: "cache", latency_ms: 8, compute_avoided: true },
        }),
      });
    }
  });
}

/**
 * Mock the paginated chat-history sync endpoint. Serves two pages:
 *   page 1 (no cursor)  → sessions p1_0 … p1_4, nextCursor = "5"
 *   page 2 (cursor=5)   → sessions p2_0 … p2_4, no nextCursor
 * POST/DELETE echo back 200. Enable via `await mockChatSync(page)` per test.
 */
export async function mockChatSync(
  page: import("@playwright/test").Page,
  syncPath = "/api/v1/chat/sessions",
) {
  function makeSessions(prefix: string, count: number, baseTs: number) {
    return Array.from({ length: count }, (_, i) => ({
      id: `${prefix}_${i}`,
      title: `${prefix.toUpperCase()} session ${i}`,
      createdAt: baseTs - i * 1000,
      updatedAt: baseTs - i * 1000,
      version: 1,
      messages: [
        {
          role: "user" as const,
          content: `${prefix} q${i}`,
          ts: baseTs - i * 1000,
        },
      ],
    }));
  }
  const page1 = makeSessions("p1", 5, 2_000_000_000_000);
  const page2 = makeSessions("p2", 5, 1_000_000_000_000);

  await page.route(`**${syncPath}**`, async (route: Route) => {
    const req = route.request();
    const method = req.method();
    const url = new URL(req.url());
    if (method === "GET") {
      const cursor = url.searchParams.get("cursor");
      if (!cursor) {
        return route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({ sessions: page1, nextCursor: "5" }),
        });
      }
      if (cursor === "5") {
        return route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({ sessions: page2, nextCursor: null }),
        });
      }
      return route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ sessions: [], nextCursor: null }),
      });
    }
    // POST / DELETE — accept.
    return route.fulfill({ status: 200, contentType: "application/json", body: "{}" });
  });
}

/**
 * Mock that forces a 409 ChatSession version conflict on the FIRST POST and
 * returns a canonical remote session containing a message the client never
 * sent (simulating another device having written first). Subsequent POSTs
 * succeed. GETs return the same canonical session in a single page.
 *
 * Used to prove the optimistic-send/rollback/de-dupe flow end to end.
 */
export async function mockChatSyncConflict(
  page: import("@playwright/test").Page,
  opts: { syncPath?: string; remoteMessage?: string } = {},
) {
  const syncPath = opts.syncPath ?? "/api/v1/chat/sessions";
  const remoteMessage = opts.remoteMessage ?? "REMOTE_WROTE_FIRST";
  let postCount = 0;
  const remoteSessionRef: { id?: string; ts?: number } = {};

  await page.route(`**${syncPath}**`, async (route: Route) => {
    const req = route.request();
    const method = req.method();
    if (method === "GET") {
      return route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ sessions: [], nextCursor: null }),
      });
    }
    if (method === "POST") {
      postCount += 1;
      const body = req.postDataJSON?.() ?? {};
      const session = body?.session ?? {};
      if (postCount === 1 && session?.id) {
        // Craft a remote session that shares one message with the client's
        // optimistic write (same key: role|ts|length) plus one exclusive
        // remote message. After merge the shared message should NOT
        // duplicate — that's the de-dupe assertion.
        const firstMsg = Array.isArray(session.messages) ? session.messages[0] : null;
        remoteSessionRef.id = session.id;
        remoteSessionRef.ts = firstMsg?.ts ?? Date.now();
        const remoteSession = {
          id: session.id,
          title: session.title ?? "New chat",
          createdAt: session.createdAt ?? Date.now(),
          updatedAt: Date.now(),
          version: (session.version ?? 1) + 5, // ahead of the client
          messages: [
            ...(firstMsg ? [firstMsg] : []),
            {
              role: "assistant" as const,
              content: remoteMessage,
              ts: (firstMsg?.ts ?? Date.now()) + 1,
            },
          ],
        };
        return route.fulfill({
          status: 409,
          contentType: "application/json",
          body: JSON.stringify({
            error: "version_conflict",
            session: remoteSession,
          }),
        });
      }
      return route.fulfill({ status: 200, contentType: "application/json", body: "{}" });
    }
    return route.fulfill({ status: 200, contentType: "application/json", body: "{}" });
  });

  return {
    getPostCount: () => postCount,
    getRemote: () => remoteSessionRef,
  };
}

/**
 * Mock that keeps returning 409 conflicts for the first `conflictCount` POSTs
 * (default 3), then accepts subsequent writes. Every 409 returns a canonical
 * remote session that shares the client's first message plus a fresh remote
 * message with a monotonically increasing version. Used to prove repeated
 * conflicts still de-duplicate the shared message, and that the merge banner
 * stays reachable across attempts.
 *
 * Also supports a "timeout" mode via `postTimeoutMs`: the Nth POST hangs long
 * enough that the client aborts. Combined, the two modes prove the UI never
 * gets stuck in an unrecoverable state.
 */
export async function mockChatSyncRepeatedConflict(
  page: import("@playwright/test").Page,
  opts: {
    syncPath?: string;
    conflictCount?: number;
    /** POST index (1-based) that should hang. Undefined = no timeout. */
    timeoutOnPost?: number;
    /** How long the timeout POST hangs before eventually 504-ing. */
    postTimeoutMs?: number;
  } = {},
) {
  const syncPath = opts.syncPath ?? "/api/v1/chat/sessions";
  const conflictCount = opts.conflictCount ?? 3;
  const timeoutOnPost = opts.timeoutOnPost;
  const postTimeoutMs = opts.postTimeoutMs ?? 4_000;
  let postCount = 0;

  await page.route(`**${syncPath}**`, async (route: Route) => {
    const req = route.request();
    const method = req.method();
    if (method === "GET") {
      return route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ sessions: [], nextCursor: null }),
      });
    }
    if (method === "POST") {
      postCount += 1;
      const idx = postCount;
      if (timeoutOnPost === idx) {
        await new Promise((r) => setTimeout(r, postTimeoutMs));
        return route.fulfill({
          status: 504,
          contentType: "application/json",
          body: JSON.stringify({ error: "gateway_timeout" }),
        });
      }
      const body = req.postDataJSON?.() ?? {};
      const session = body?.session ?? {};
      if (idx <= conflictCount && session?.id) {
        const firstMsg = Array.isArray(session.messages) ? session.messages[0] : null;
        const remoteSession = {
          id: session.id,
          title: session.title ?? "New chat",
          createdAt: session.createdAt ?? Date.now(),
          updatedAt: Date.now(),
          version: (session.version ?? 1) + 5 * idx,
          messages: [
            ...(firstMsg ? [firstMsg] : []),
            {
              role: "assistant" as const,
              content: `remote-attempt-${idx}`,
              ts: (firstMsg?.ts ?? Date.now()) + idx,
            },
          ],
        };
        return route.fulfill({
          status: 409,
          contentType: "application/json",
          body: JSON.stringify({
            error: "version_conflict",
            session: remoteSession,
          }),
        });
      }
      return route.fulfill({ status: 200, contentType: "application/json", body: "{}" });
    }
    return route.fulfill({ status: 200, contentType: "application/json", body: "{}" });
  });

  return { getPostCount: () => postCount };
}

/**
 * Capture every POST to /api/telemetry (both fetch and sendBeacon land here)
 * and expose the parsed event payloads. Returns a `getEvents()` helper.
 */
export async function mockTelemetry(page: import("@playwright/test").Page) {
  const events: Array<Record<string, unknown>> = [];
  await page.route("**/api/telemetry", async (route: Route) => {
    try {
      const body = route.request().postData();
      if (body) {
        const parsed = JSON.parse(body);
        if (Array.isArray(parsed?.events)) {
          for (const e of parsed.events) events.push(e);
        } else if (parsed && typeof parsed === "object") {
          events.push(parsed);
        }
      }
    } catch {
      /* ignore parse errors */
    }
    await route.fulfill({ status: 204, body: "" });
  });
  return {
    getEvents: () => events.slice(),
    getEventsOfKind: (kind: string) => events.filter((e) => (e as { kind?: string }).kind === kind),
  };
}
