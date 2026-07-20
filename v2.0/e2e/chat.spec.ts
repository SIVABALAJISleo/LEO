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

test.describe("chat flow", () => {
  test.beforeEach(async ({ page }) => {
    await mockLeoBackend(page);
    await seedAuth(page);
  });

  test("streams an assistant reply end-to-end", async ({ page }) => {
    await page.goto("/app/chat");
    await expect(page.getByRole("heading", { name: /chat/i })).toBeVisible();

    const input = page.getByTestId("chat-input");
    await input.fill("Hello LEO");
    await page.getByTestId("chat-send").click();

    await expect(page.getByTestId("chat-stop")).toBeVisible({ timeout: 5_000 });
    const assistant = page.getByTestId("chat-assistant").last();
    await expect(assistant).toContainText("Hello from LEO.", { timeout: 10_000 });
    await expect(page.getByTestId("chat-send")).toBeVisible({ timeout: 5_000 });
  });
});

test.describe("chat history pagination", () => {
  test.beforeEach(async ({ page }) => {
    await mockLeoBackend(page);
    await mockChatSync(page);
    await seedAuth(page);
    await enableSync(page);
  });

  test("Load more fetches the next cursor page", async ({ page }) => {
    await page.goto("/app/chat");
    const mod = process.platform === "darwin" ? "Meta" : "Control";
    await page.keyboard.press(`${mod}+K`);
    const historyPanel = page.getByLabel("Chat history");
    await expect(historyPanel).toBeVisible();

    await expect(historyPanel.getByText("P1 session 0")).toBeVisible({ timeout: 10_000 });
    await expect(historyPanel.getByText("P1 session 4")).toBeVisible();
    await expect(historyPanel.getByText("P2 session 0")).toHaveCount(0);

    const loadMore = page.getByTestId("history-load-more");
    await expect(loadMore).toBeVisible();
    await loadMore.click();

    await expect(historyPanel.getByText("P2 session 0")).toBeVisible({ timeout: 10_000 });
    await expect(historyPanel.getByText("P2 session 4")).toBeVisible();
    await expect(loadMore).toHaveCount(0);
  });

  test("keyboard-selected conversation stays consistent across pages", async ({ page }) => {
    await page.goto("/app/chat");
    const mod = process.platform === "darwin" ? "Meta" : "Control";

    await page.keyboard.press(`${mod}+K`);
    const historyPanel = page.getByLabel("Chat history");
    await expect(historyPanel.getByText("P1 session 0")).toBeVisible({ timeout: 10_000 });
    await page.getByTestId("history-load-more").click();
    await expect(historyPanel.getByText("P2 session 0")).toBeVisible({ timeout: 10_000 });

    await page.getByLabel("Search conversations").focus();
    // ArrowDown 6× → across the page-1/page-2 boundary (index 6 = P2 session 1).
    for (let i = 0; i < 6; i += 1) {
      await page.keyboard.press("ArrowDown");
    }
    await page.keyboard.press("Enter");

    await expect(historyPanel).toBeHidden({ timeout: 5_000 });
    // Seeded message content proves the right entry was selected across the page boundary.
    await expect(page.getByText("p2 q1", { exact: true })).toBeVisible();

    // Reopen — selection persists as aria-current active row.
    await page.keyboard.press(`${mod}+K`);
    const activeItem = historyPanel.locator('[aria-current="true"]');
    await expect(activeItem).toHaveText(/P2 session 1/);
  });
});
