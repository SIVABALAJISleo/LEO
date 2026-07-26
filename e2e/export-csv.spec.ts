import { test, expect } from "@playwright/test";
import { mockLeoBackend, mockChatSync } from "./mocks";
import { freezeNonVisual } from "./deterministic";

async function seedAuth(page: import("@playwright/test").Page) {
  await page.addInitScript(() => {
    window.localStorage.setItem("leo.jwt", "test-jwt-token-abcdef");
    window.localStorage.setItem("leo.chat.sync", "on");
    window.localStorage.setItem("leo.chat.sync_path", "/api/v1/chat/sessions");
  });
}

test.describe("chat history — export-to-CSV across every cursor page", () => {
  test.beforeEach(async ({ page }) => {
    await freezeNonVisual(page);
    await mockLeoBackend(page);
    await mockChatSync(page);
    await seedAuth(page);
  });

  test("CSV export contains all cursor pages with unique rows keyed by session id", async ({
    page,
  }) => {
    await page.goto("/app/chat");
    const mod = process.platform === "darwin" ? "Meta" : "Control";
    // Open history so the first page is guaranteed to be loaded before we export.
    await page.keyboard.press(`${mod}+K`);
    await expect(page.getByLabel("Chat history").getByText("P1 session 0")).toBeVisible({
      timeout: 10_000,
    });

    const downloadPromise = page.waitForEvent("download");
    await page.getByTestId("chat-export-csv").click();
    const download = await downloadPromise;

    expect(download.suggestedFilename()).toMatch(/\.csv$/);

    const stream = await download.createReadStream();
    const chunks: Buffer[] = [];
    for await (const chunk of stream) chunks.push(Buffer.from(chunk));
    const text = Buffer.concat(chunks).toString("utf8");

    const lines = text.trim().split("\n");
    const header = lines[0]!.split(",");
    expect(header).toEqual([
      "id",
      "title",
      "created_at",
      "updated_at",
      "version",
      "message_count",
      "transcript",
    ]);

    // First column of every non-header line is the session id.
    // (safe: our mock ids never contain commas or quotes.)
    const idColumn = lines.slice(1).map((l) => l.split(",")[0]);

    // Uniqueness: every session id appears exactly once even though the
    // sidebar has only lazy-loaded page 1 so far — the export walker must
    // pull page 2 too and dedupe by id.
    expect(new Set(idColumn).size).toBe(idColumn.length);

    for (let i = 0; i < 5; i += 1) {
      expect(idColumn).toContain(`p1_${i}`);
      expect(idColumn).toContain(`p2_${i}`);
    }
    expect(idColumn.length).toBeGreaterThanOrEqual(10);
  });
});
