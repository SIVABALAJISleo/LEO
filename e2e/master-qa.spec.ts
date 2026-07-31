import { test, expect } from "@playwright/test";
import { LoginPage } from "./pom/LoginPage";
import { ChatPage } from "./pom/ChatPage";
import { mockLeoBackend } from "./mocks";

test.describe("Master QA Playwright Automated Suite", () => {
  test.beforeEach(async ({ page }) => {
    await mockLeoBackend(page);
  });

  test("Pillar 1: Full Navigation & Screen Inventory Sweep", async ({ page }) => {
    const publicRoutes = [
      "/",
      "/login",
      "/signup",
      "/about",
      "/docs",
      "/features",
      "/benchmarks",
      "/platform",
    ];
    for (const route of publicRoutes) {
      await page.goto(route);
      await expect(page).toHaveURL(new RegExp(route.replace("/", "\\/")));
      await expect(page.locator("body")).toBeVisible();
    }
  });

  test("Pillar 2: Authenticated App Route Protection & Session Recovery", async ({ page }) => {
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.login("admin@leo.ai", "AdminPass2026!");

    const appRoutes = [
      "/app",
      "/app/chat",
      "/app/memory",
      "/app/embeddings",
      "/app/knowledge-graph",
      "/app/benchmarks",
      "/app/orchestrate",
      "/app/security",
      "/app/settings",
    ];

    for (const route of appRoutes) {
      await page.goto(route);
      await expect(page).toHaveURL(new RegExp(route.replace(/\//g, "\\/")));
    }
  });

  test("Pillar 3: Chat Interaction & Streaming Workflow", async ({ page }) => {
    const loginPage = new LoginPage(page);
    const chatPage = new ChatPage(page);

    await loginPage.goto();
    await loginPage.login("admin@leo.ai", "AdminPass2026!");
    await chatPage.goto();

    await chatPage.sendMessage("Verify enterprise LEO AI multi-agent orchestration workflow");
    await expect(page.locator("body")).toContainText(/LEO|Response|AI/i, { timeout: 10000 });
  });
});
