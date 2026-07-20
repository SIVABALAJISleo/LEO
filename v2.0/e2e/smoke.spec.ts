import { test, expect } from "@playwright/test";

/**
 * Smoke test used by CI against a deployed preview.
 * Set SMOKE_BASE_URL (or E2E_BASE_URL) to point at the running artifact.
 */
const target = process.env.SMOKE_BASE_URL ?? process.env.E2E_BASE_URL;

test.describe("deployment smoke", () => {
  test.skip(!target, "SMOKE_BASE_URL / E2E_BASE_URL not set");

  test("home page renders", async ({ page }) => {
    const res = await page.goto(target!, { waitUntil: "domcontentloaded" });
    expect(res?.ok(), `HTTP ${res?.status()}`).toBeTruthy();
    await expect(page).toHaveTitle(/LEO AI/i);
  });

  test("/app redirects unauthenticated to /login", async ({ page }) => {
    await page.goto(`${target}/app`);
    await expect(page).toHaveURL(/\/login/);
  });

  test("marketing routes respond 200", async ({ request }) => {
    for (const path of ["/", "/platform", "/features", "/benchmarks", "/docs", "/about"]) {
      const r = await request.get(`${target}${path}`);
      expect(r.status(), `${path} → ${r.status()}`).toBeLessThan(400);
    }
  });
});
