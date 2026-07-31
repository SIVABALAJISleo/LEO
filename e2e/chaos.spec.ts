import { test, expect } from "@playwright/test";

const PAYLOADS = [
  // SQL Injection
  "' OR 1=1 --",
  "admin' --",
  "'; DROP TABLE users; --",
  // XSS
  "<script>alert(1)</script>",
  '"><img src=x onerror=alert(1)>',
  // Boundary / Null
  "",
  "   ",
  // Huge text / Unicode
  "A".repeat(10000),
  "😂🔥".repeat(100),
  "\\u0000",
  // Negative/Floats
  "-1",
  "999999999999999999999999999",
];

test.describe("Phase 5 & 11: Security & Fuzzing", () => {
  test("Fuzz Login Form", async ({ page }) => {
    await page.goto("/login");
    const emailInput = page.getByLabel(/email/i).first();
    const passwordInput = page.getByLabel(/password/i).first();
    const submitButton = page.getByRole("button", { name: /sign in|log in/i }).first();

    for (const payload of PAYLOADS) {
      // Fuzz Email
      await emailInput.fill(payload);
      await passwordInput.fill("SecurePass123!");
      await submitButton.click();

      // Wait a moment for UI to settle, we expect it NOT to crash
      await page.waitForTimeout(100);

      // Fuzz Password
      await emailInput.fill("test@hyper.local");
      await passwordInput.fill(payload);
      await submitButton.click();

      await page.waitForTimeout(100);

      // Ensure the page hasn't crashed (White screen of death)
      const isVisible = await emailInput.isVisible();
      expect(isVisible).toBeTruthy();
    }
  });
});

test.describe("Phase 15 & 16: Network & Chaos Engineering", () => {
  test("Random network disconnection and race condition hunting", async ({ page, context }) => {
    await page.goto("/login");

    // Simulate sudden 99% packet loss / offline state
    await context.setOffline(true);

    // Spam click to find race conditions
    const submitButton = page.getByRole("button", { name: /sign in|log in/i }).first();

    for (let i = 0; i < 20; i++) {
      await submitButton.click({ force: true });
    }

    // Bring network back online
    await context.setOffline(false);
    await submitButton.click({ force: true });

    // Verify application did not fatally freeze
    const isVisible = await submitButton.isVisible();
    expect(isVisible).toBeTruthy();
  });
});
