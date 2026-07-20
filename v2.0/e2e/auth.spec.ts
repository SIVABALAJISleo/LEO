import { test, expect } from "@playwright/test";
import { mockLeoBackend } from "./mocks";

test.describe("auth + protected route", () => {
  test.beforeEach(async ({ page }) => {
    await mockLeoBackend(page);
  });

  test("login redirects to /app and gates unauthenticated access", async ({ page, context }) => {
    // Unauthenticated visit to /app should redirect to /login
    await page.goto("/app");
    await expect(page).toHaveURL(/\/login/);

    // Fill in credentials and submit
    await page.getByLabel(/email/i).fill("test@leo.ai");
    await page.getByLabel(/password/i).fill("password123");
    await page.getByRole("button", { name: /sign in|log in/i }).click();

    // Should land on /app after login
    await expect(page).toHaveURL(/\/app/, { timeout: 10_000 });

    // Token persists across reload
    const storage = await context.storageState();
    const origin = storage.origins.find(
      (o) => o.origin.includes("localhost") || o.origin.includes("127.0.0.1"),
    );
    expect(origin?.localStorage.some((kv) => kv.name === "leo.jwt")).toBeTruthy();
  });
});
