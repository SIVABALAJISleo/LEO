import { test, expect } from "@playwright/test";

/**
 * Live-backend Playwright suite. Runs only when E2E_LIVE=1.
 * Uses real network calls against LEO_API_BASE_URL with real credentials.
 *
 * Required env:
 *   E2E_LIVE=1
 *   E2E_BASE_URL=<deployed frontend url>   (playwright reuses this baseURL)
 *   LEO_API_BASE_URL=<backend url>         (injected into localStorage)
 *   LEO_TEST_EMAIL=<user email>
 *   LEO_TEST_PASSWORD=<user password>
 * Optional:
 *   LEO_TEST_JWT=<pre-minted jwt>          (skips login form, seeds token)
 *   LEO_TEST_CHAT_PROMPT="Ping"            (defaults to a quick health prompt)
 */
const live = process.env.E2E_LIVE === "1";
const apiBase = process.env.LEO_API_BASE_URL ?? "";
const email = process.env.LEO_TEST_EMAIL ?? "";
const password = process.env.LEO_TEST_PASSWORD ?? "";
const preToken = process.env.LEO_TEST_JWT ?? "";
const prompt = process.env.LEO_TEST_CHAT_PROMPT ?? "Ping — respond with 'pong'.";

test.describe("live backend", () => {
  test.skip(!live, "Set E2E_LIVE=1 with LEO_API_BASE_URL + credentials to run.");
  test.skip(!apiBase, "LEO_API_BASE_URL is required.");
  test.skip(!preToken && (!email || !password), "Provide LEO_TEST_JWT or email/password.");

  test.beforeEach(async ({ page }) => {
    // Point the frontend at the real backend before any code runs.
    await page.addInitScript((base: string) => {
      window.localStorage.setItem("leo.api_base", base);
    }, apiBase);
    if (preToken) {
      await page.addInitScript((t: string) => {
        window.localStorage.setItem("leo.jwt", t);
      }, preToken);
    }
  });

  test("backend health responds", async ({ request }) => {
    // Try common health paths — first that returns 200 wins.
    const candidates = ["/health", "/healthz", "/api/v1/leo/metrics"];
    let ok = false;
    for (const path of candidates) {
      const res = await request.get(`${apiBase}${path}`).catch(() => null);
      if (res && res.ok()) {
        ok = true;
        break;
      }
    }
    expect(ok, `no health endpoint answered on ${apiBase}`).toBeTruthy();
  });

  test("login (or seeded JWT) opens /app", async ({ page }) => {
    if (preToken) {
      await page.goto("/app");
    } else {
      await page.goto("/login");
      await page.getByLabel(/email/i).fill(email);
      await page.getByLabel(/password/i).fill(password);
      await page.getByRole("button", { name: /sign in|log in/i }).click();
    }
    await expect(page).toHaveURL(/\/app/, { timeout: 20_000 });
  });

  test("chat round-trip against real backend", async ({ page }) => {
    if (!preToken) {
      await page.goto("/login");
      await page.getByLabel(/email/i).fill(email);
      await page.getByLabel(/password/i).fill(password);
      await page.getByRole("button", { name: /sign in|log in/i }).click();
      await expect(page).toHaveURL(/\/app/, { timeout: 20_000 });
    }
    await page.goto("/app/chat");
    const input = page.getByTestId("chat-input");
    await input.fill(prompt);
    await page.getByTestId("chat-send").click();
    // Expect an assistant bubble to appear + eventually contain non-empty text.
    const assistant = page.getByTestId("chat-assistant").last();
    await expect(assistant).toBeVisible({ timeout: 30_000 });
    await expect
      .poll(async () => (await assistant.innerText()).trim().length, { timeout: 60_000 })
      .toBeGreaterThan(0);
  });

  test("chat history sync: POST, GET, DELETE round-trip", async ({ page, request }) => {
    test.skip(!preToken, "Provide LEO_TEST_JWT to hit the sync endpoints directly.");
    const syncPath = process.env.LEO_TEST_SYNC_PATH ?? "/api/v1/chat/sessions";
    const id = `e2e_${Date.now()}`;
    const session = {
      id,
      title: "E2E sync smoke",
      createdAt: Date.now(),
      updatedAt: Date.now(),
      version: 1,
      messages: [{ role: "user", content: "ping", ts: Date.now() }],
    };

    // POST
    const post = await request.post(`${apiBase}${syncPath}`, {
      headers: { Authorization: `Bearer ${preToken}`, "Content-Type": "application/json" },
      data: { session, expectedVersion: 0 },
    });
    expect(post.ok(), `POST ${syncPath} failed (${post.status()})`).toBeTruthy();

    // GET (paginated)
    const list = await request.get(`${apiBase}${syncPath}?limit=200`, {
      headers: { Authorization: `Bearer ${preToken}` },
    });
    expect(list.ok(), `GET ${syncPath} failed (${list.status()})`).toBeTruthy();
    const body = await list.json();
    const sessions = Array.isArray(body) ? body : (body.sessions ?? body.items ?? []);
    expect(sessions.some((s: { id: string }) => s.id === id)).toBeTruthy();

    // Confirm the frontend surfaces it after enabling sync.
    await page.addInitScript(
      (path: string) => {
        window.localStorage.setItem("leo.chat.sync", "on");
        window.localStorage.setItem("leo.chat.sync_path", path);
      },
      syncPath,
    );
    await page.goto("/app/chat");
    // Open history panel via ⌘/Ctrl+K.
    const isMac = process.platform === "darwin";
    await page.keyboard.press(isMac ? "Meta+K" : "Control+K");
    await expect(page.getByText("E2E sync smoke")).toBeVisible({ timeout: 15_000 });

    // DELETE
    const del = await request.delete(`${apiBase}${syncPath}/${id}`, {
      headers: { Authorization: `Bearer ${preToken}` },
    });
    expect(del.ok(), `DELETE ${syncPath}/${id} failed (${del.status()})`).toBeTruthy();
  });

  test("keyboard navigation opens history, selects with arrows, opens with Enter", async ({
    page,
  }) => {
    if (!preToken) {
      await page.goto("/login");
      await page.getByLabel(/email/i).fill(email);
      await page.getByLabel(/password/i).fill(password);
      await page.getByRole("button", { name: /sign in|log in/i }).click();
      await expect(page).toHaveURL(/\/app/, { timeout: 20_000 });
    }
    await page.goto("/app/chat");

    // Seed at least one saved conversation via the send flow.
    await page.getByTestId("chat-input").fill("Keyboard nav check — respond briefly.");
    await page.getByTestId("chat-send").click();
    await expect(page.getByTestId("chat-assistant").last()).toBeVisible({ timeout: 60_000 });

    const isMac = process.platform === "darwin";
    // ⌘/Ctrl+K → open history + focus search
    await page.keyboard.press(isMac ? "Meta+K" : "Control+K");
    const search = page.getByLabel("Search conversations");
    await expect(search).toBeFocused();

    // Arrow down + Enter should load the top conversation.
    await page.keyboard.press("ArrowDown");
    await page.keyboard.press("Enter");
    // History closes after selection.
    await expect(page.getByLabel("Chat history")).toBeHidden({ timeout: 5_000 });

    // ⌘/Ctrl+Shift+N → new chat clears the transcript.
    await page.keyboard.press(isMac ? "Meta+Shift+N" : "Control+Shift+N");
    await expect(page.getByText("Start a conversation")).toBeVisible();
  });

  test("manual reconnect button restarts a dropped stream", async ({ page }) => {
    if (!preToken) {
      await page.goto("/login");
      await page.getByLabel(/email/i).fill(email);
      await page.getByLabel(/password/i).fill(password);
      await page.getByRole("button", { name: /sign in|log in/i }).click();
      await expect(page).toHaveURL(/\/app/, { timeout: 20_000 });
    }
    await page.goto("/app/chat");
    await page.getByTestId("chat-input").fill("Say a long paragraph so I can interrupt.");
    await page.getByTestId("chat-send").click();

    // Force-drop by going offline mid-stream, then back online + manual reconnect.
    const assistant = page.getByTestId("chat-assistant").last();
    await expect(assistant).toBeVisible({ timeout: 30_000 });
    await page.context().setOffline(true);
    // Wait for either the auto-reconnect banner or the manual card to surface.
    const reconnectBanner = page
      .getByTestId("chat-reconnecting")
      .or(page.getByTestId("chat-reconnect-manual"));
    await expect(reconnectBanner).toBeVisible({ timeout: 30_000 });
    await page.context().setOffline(false);
    await page.getByRole("button", { name: /reconnect/i }).first().click();
    await expect
      .poll(async () => (await assistant.innerText()).trim().length, { timeout: 60_000 })
      .toBeGreaterThan(0);
  });
});
