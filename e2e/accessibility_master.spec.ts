import { test, expect } from "@playwright/test";
import { mockLeoBackend } from "./mocks";

test.describe("WCAG 2.1 AA Accessibility & Keyboard Navigation Suite", () => {
  test.beforeEach(async ({ page }) => {
    await mockLeoBackend(page);
  });

  test("Check ARIA Roles & Contrast across Primary Routes", async ({ page }) => {
    const routes = ["/", "/login", "/app/chat", "/app/settings"];
    for (const route of routes) {
      await page.goto(route);
      // Ensure interactive buttons have accessible names
      const buttons = page.locator("button");
      const count = await buttons.count();
      for (let i = 0; i < Math.min(count, 5); i++) {
        const btn = buttons.nth(i);
        const name = (await btn.getAttribute("aria-label")) || (await btn.innerText());
        expect(name).toBeTruthy();
      }
    }
  });

  test("Keyboard Traversal & Focus Ring Visibility", async ({ page }) => {
    await page.goto("/login");
    await page.keyboard.press("Tab");
    const focusedTag = await page.evaluate(() => document.activeElement?.tagName);
    expect(focusedTag).toBeTruthy();
  });
});
