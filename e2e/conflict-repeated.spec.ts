import { test, expect } from "@playwright/test";
import { mockLeoBackend, mockChatSyncRepeatedConflict, mockTelemetry } from "./mocks";
import { freezeNonVisual } from "./deterministic";

async function seedAuth(page: import("@playwright/test").Page) {
  await page.addInitScript(() => {
    window.localStorage.setItem("leo.jwt", "test-jwt-token-abcdef");
    window.localStorage.setItem("leo.chat.sync", "on");
    window.localStorage.setItem("leo.chat.sync_path", "/api/v1/chat/sessions");
  });
}

test.describe("chat sync — repeated 409s + server timeout stay recoverable", () => {
  test.beforeEach(async ({ page }) => {
    await freezeNonVisual(page);
    await mockLeoBackend(page);
    await seedAuth(page);
  });

  test("three back-to-back 409s de-duplicate the shared user message", async ({ page }) => {
    const telemetry = await mockTelemetry(page);
    const conflict = await mockChatSyncRepeatedConflict(page, {
      conflictCount: 3,
    });

    await page.goto("/app/chat");
    await expect(page.getByRole("heading", { name: /chat/i })).toBeVisible();

    // Three optimistic sends in a row — each one races a 409.
    for (let i = 0; i < 3; i += 1) {
      await page.getByTestId("chat-input").fill(`echo ${i}`);
      await page.getByTestId("chat-send").click();
      await expect(page.getByTestId("chat-assistant").last()).toContainText("Hello from LEO.", {
        timeout: 10_000,
      });
      await expect(page.getByTestId("chat-send")).toBeVisible({ timeout: 5_000 });
    }

    // The merge banner must have surfaced at least once for the conflict
    // rollback kind — proves the UI reached a clear recoverable state.
    await expect
      .poll(
        () =>
          telemetry
            .getEventsOfKind("chat-merge-banner")
            .filter((e) => (e as { merge_kind?: string }).merge_kind === "conflict-rollback")
            .length,
        { timeout: 10_000 },
      )
      .toBeGreaterThanOrEqual(1);

    // Every user echo should render exactly once — no double-render from the
    // 3 rounds of merges.
    for (let i = 0; i < 3; i += 1) {
      await expect(page.getByText(`echo ${i}`, { exact: true })).toHaveCount(1);
    }

    // At least one remote-only assistant reply from the merges shows up.
    await expect(page.getByText(/remote-attempt-\d+/).first()).toBeVisible();

    // Rollback telemetry fired at least three times (one per conflict).
    expect(telemetry.getEventsOfKind("chat-optimistic-rollback").length).toBeGreaterThanOrEqual(3);
    expect(conflict.getPostCount()).toBeGreaterThanOrEqual(3);
  });

  test("server timeout surfaces a recoverable UI without losing the user message", async ({
    page,
  }) => {
    // First POST hangs 4s → client / UI should not wedge. Follow-up POSTs
    // succeed so retry paths remain viable.
    await mockChatSyncRepeatedConflict(page, {
      conflictCount: 0,
      timeoutOnPost: 1,
      postTimeoutMs: 4_000,
    });

    await page.goto("/app/chat");
    await page.getByTestId("chat-input").fill("timeout me");
    await page.getByTestId("chat-send").click();

    // Assistant streamed reply completes (LLM call is independent of sync).
    await expect(page.getByTestId("chat-assistant").last()).toContainText("Hello from LEO.", {
      timeout: 10_000,
    });

    // The optimistic user bubble is still on screen and NOT duplicated
    // while the sync POST is still in flight.
    await expect(page.getByText("timeout me", { exact: true })).toHaveCount(1);

    // Input + send are re-enabled — the UI is not stuck in a submitting state.
    await expect(page.getByTestId("chat-send")).toBeVisible({ timeout: 5_000 });
    await expect(page.getByTestId("chat-input")).toBeEnabled();
  });
});
