import { test, expect } from "@playwright/test";
import { mockLeoBackend, mockChatSyncConflict, mockTelemetry } from "./mocks";

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

test.describe("chat 409 conflict — optimistic rollback + de-dupe", () => {
  test.beforeEach(async ({ page }) => {
    await mockLeoBackend(page);
    await seedAuth(page);
    await enableSync(page);
  });

  test("optimistic message is rolled back and merged without duplicates", async ({
    page,
  }) => {
    const telemetry = await mockTelemetry(page);
    const conflict = await mockChatSyncConflict(page, {
      remoteMessage: "reply-from-other-device",
    });

    await page.goto("/app/chat");
    await expect(page.getByRole("heading", { name: /chat/i })).toBeVisible();

    // Optimistic send — the user bubble appears immediately.
    await page.getByTestId("chat-input").fill("Hello LEO");
    await page.getByTestId("chat-send").click();

    // Streamed reply completes first.
    const assistant = page.getByTestId("chat-assistant").last();
    await expect(assistant).toContainText("Hello from LEO.", { timeout: 10_000 });
    await expect(page.getByTestId("chat-send")).toBeVisible({ timeout: 5_000 });

    // Now the client POSTs to /api/v1/chat/sessions and gets a 409 with the
    // canonical remote session containing an exclusive assistant reply.
    // The merge banner surfaces the reconciliation.
    const banner = page.getByTestId("chat-merge-banner");
    await expect(banner).toBeVisible({ timeout: 10_000 });
    await expect(banner).toContainText(/Sync conflict resolved/i);

    // The remote-only message is now rendered in the conversation.
    await expect(page.getByText("reply-from-other-device")).toBeVisible();

    // De-dupe: the original user message still appears exactly once — the
    // 409 merge must not double-render the message that was in both copies.
    await expect(page.getByText("Hello LEO", { exact: true })).toHaveCount(1);

    // Telemetry: an optimistic-rollback event fires and reports how many
    // messages were reconciled from the remote copy.
    await expect
      .poll(() => telemetry.getEventsOfKind("chat-optimistic-rollback").length, {
        timeout: 5_000,
      })
      .toBeGreaterThan(0);
    const rollback = telemetry.getEventsOfKind("chat-optimistic-rollback")[0] as {
      reconciled_from_remote?: number;
    };
    expect(rollback.reconciled_from_remote).toBeGreaterThanOrEqual(1);

    // Merge-banner telemetry also fires and carries the conflict-rollback kind.
    const bannerEvents = telemetry.getEventsOfKind("chat-merge-banner") as Array<{
      merge_kind?: string;
    }>;
    expect(bannerEvents.some((e) => e.merge_kind === "conflict-rollback")).toBe(
      true,
    );

    // The 409-triggering POST actually happened.
    expect(conflict.getPostCount()).toBeGreaterThanOrEqual(1);
  });
});
