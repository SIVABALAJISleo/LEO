import { test, expect } from "@playwright/test";
import { mockLeoBackend, mockChatSync } from "./mocks";

async function seedAuth(page: import("@playwright/test").Page) {
  await page.addInitScript(() => {
    window.localStorage.setItem("leo.jwt", "test-jwt-token-abcdef");
  });
}

async function enableSync(page: import("@playwright/test").Page) {
  await page.addInitScript(() => {
    window.localStorage.setItem("leo.chat.sync", "on");
    window.localStorage.setItem("leo.chat.sync_path", "/api/v1/chat/sessions");
  });
}

test.describe("chat history — export all across cursor pages", () => {
  test.beforeEach(async ({ page }) => {
    await mockLeoBackend(page);
    await mockChatSync(page);
    await seedAuth(page);
    await enableSync(page);
  });

  test("export-all pulls every cursor page and writes them into the JSON blob", async ({
    page,
  }) => {
    await page.goto("/app/chat");
    const mod = process.platform === "darwin" ? "Meta" : "Control";

    // Open history so we can see the first page loaded — proves sync is live.
    await page.keyboard.press(`${mod}+K`);
    const historyPanel = page.getByLabel("Chat history");
    await expect(historyPanel.getByText("P1 session 0")).toBeVisible({
      timeout: 10_000,
    });
    // Sanity — page 2 has NOT been lazy-loaded into the sidebar yet.
    await expect(historyPanel.getByText("P2 session 0")).toHaveCount(0);

    // Intercept the download triggered by exportAll.
    const downloadPromise = page.waitForEvent("download");
    await page.keyboard.press(`${mod}+E`);
    const download = await downloadPromise;

    const stream = await download.createReadStream();
    const chunks: Buffer[] = [];
    for await (const chunk of stream) chunks.push(Buffer.from(chunk));
    const text = Buffer.concat(chunks).toString("utf8");
    const parsed = JSON.parse(text) as {
      exported_at: string;
      sessions: Array<{ id: string; title: string }>;
    };

    expect(typeof parsed.exported_at).toBe("string");
    // Both cursor pages must be present in the export — 5 from page 1 + 5 from page 2.
    const titles = parsed.sessions.map((s) => s.title);
    for (let i = 0; i < 5; i += 1) {
      expect(titles).toContain(`P1 session ${i}`);
      expect(titles).toContain(`P2 session ${i}`);
    }
    // De-duplicated by id — no session appears twice.
    const ids = parsed.sessions.map((s) => s.id);
    expect(new Set(ids).size).toBe(ids.length);
    expect(parsed.sessions.length).toBeGreaterThanOrEqual(10);
  });
});
