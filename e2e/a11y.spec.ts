import { test, expect } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import { mockLeoBackend, mockChatSync } from "./mocks";
import { freezeNonVisual } from "./deterministic";

async function seedAuth(page: import("@playwright/test").Page) {
  await page.addInitScript(() => {
    window.localStorage.setItem("leo.jwt", "test-jwt-token-abcdef");
    window.localStorage.setItem("leo.chat.sync", "on");
    window.localStorage.setItem("leo.chat.sync_path", "/api/v1/chat/sessions");
  });
}

const BREAKPOINTS = [
  { name: "mobile", width: 390, height: 844 },
  { name: "tablet", width: 820, height: 1180 },
  { name: "desktop", width: 1440, height: 900 },
] as const;

test.describe("chat page — axe-core accessibility across breakpoints", () => {
  test.beforeEach(async ({ page }) => {
    await freezeNonVisual(page);
    await mockLeoBackend(page);
    await mockChatSync(page);
    await seedAuth(page);
  });

  for (const bp of BREAKPOINTS) {
    test(`chat empty state passes axe @ ${bp.name}`, async ({ page }) => {
      await page.setViewportSize({ width: bp.width, height: bp.height });
      await page.goto("/app/chat");
      await expect(page.getByRole("heading", { name: /start a conversation/i })).toBeVisible();

      const results = await new AxeBuilder({ page })
        .withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"])
        // Color contrast is enforced by the design system tokens tested
        // separately in visual regression — skip only when noisy on
        // synthetic offscreen icons.
        .disableRules(["region"])
        .analyze();

      // Attach the raw report so CI can surface offenders on failure.
      await test.info().attach(`axe-${bp.name}.json`, {
        body: JSON.stringify(results.violations, null, 2),
        contentType: "application/json",
      });
      expect(
        results.violations,
        results.violations.map((v) => `${v.id} — ${v.help} (${v.nodes.length})`).join("\n"),
      ).toEqual([]);
    });

    test(`chat with reply passes axe @ ${bp.name}`, async ({ page }) => {
      await page.setViewportSize({ width: bp.width, height: bp.height });
      await page.goto("/app/chat");
      await page.getByTestId("chat-input").fill("hello");
      await page.getByTestId("chat-send").click();
      await expect(page.getByTestId("chat-assistant").last()).toContainText("Hello from LEO.", {
        timeout: 10_000,
      });
      await expect(page.getByTestId("chat-send")).toBeVisible({ timeout: 5_000 });

      const results = await new AxeBuilder({ page })
        .withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"])
        .disableRules(["region"])
        .analyze();
      await test.info().attach(`axe-reply-${bp.name}.json`, {
        body: JSON.stringify(results.violations, null, 2),
        contentType: "application/json",
      });
      expect(
        results.violations,
        results.violations.map((v) => `${v.id} — ${v.help} (${v.nodes.length})`).join("\n"),
      ).toEqual([]);
    });
  }
});
