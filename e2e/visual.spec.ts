import { test, expect } from "@playwright/test";
import { mockLeoBackend, mockChatSync } from "./mocks";
import { freezeNonVisual } from "./deterministic";

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

// Snapshots are stored under e2e/__screenshots__/visual.spec.ts-snapshots/.
// Regenerate locally with: `bunx playwright test e2e/visual.spec.ts --update-snapshots`.
const BREAKPOINTS = [
  { name: "mobile", width: 390, height: 844 },
  { name: "tablet", width: 820, height: 1180 },
  { name: "desktop", width: 1440, height: 900 },
] as const;

test.describe("chat layout — NVIDIA-inspired visual regression", () => {
  test.beforeEach(async ({ page }) => {
    // Freeze clocks / RNG / animations so snapshots are stable without
    // masking large slices of the UI.
    await freezeNonVisual(page);
    await mockLeoBackend(page);
    await mockChatSync(page);
    await seedAuth(page);
    await enableSync(page);
  });

  for (const bp of BREAKPOINTS) {
    test(`chat empty state @ ${bp.name} (${bp.width}x${bp.height})`, async ({
      page,
    }) => {
      await page.setViewportSize({ width: bp.width, height: bp.height });
      await page.goto("/app/chat");
      await expect(
        page.getByRole("heading", { name: /start a conversation/i }),
      ).toBeVisible();
      // Wait for fonts + any async layout to settle.
      await page.evaluate(() => document.fonts?.ready);
      await expect(page).toHaveScreenshot(`chat-empty-${bp.name}.png`, {
        fullPage: true,
        animations: "disabled",
        // Timestamps + live regions change between runs; mask them out.
        mask: [
          page.getByTestId("chat-live-region"),
          page.locator("time"),
          page.locator("[data-history-list] .font-mono"),
        ],
        maxDiffPixelRatio: 0.02,
      });
    });

    test(`chat after streamed reply @ ${bp.name}`, async ({ page }) => {
      await page.setViewportSize({ width: bp.width, height: bp.height });
      await page.goto("/app/chat");
      await page.getByTestId("chat-input").fill("Snapshot me");
      await page.getByTestId("chat-send").click();
      const assistant = page.getByTestId("chat-assistant").last();
      await expect(assistant).toContainText("Hello from LEO.", { timeout: 10_000 });
      await expect(page.getByTestId("chat-send")).toBeVisible({ timeout: 5_000 });
      await page.evaluate(() => document.fonts?.ready);
      await expect(page).toHaveScreenshot(`chat-reply-${bp.name}.png`, {
        fullPage: true,
        animations: "disabled",
        mask: [
          page.getByTestId("chat-live-region"),
          page.locator("time"),
          page.locator(".font-mono"),
        ],
        maxDiffPixelRatio: 0.02,
      });
    });
  }
});
