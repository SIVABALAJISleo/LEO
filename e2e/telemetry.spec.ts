import { test, expect } from "@playwright/test";
import { mockLeoBackend, mockTelemetry } from "./mocks";

async function seedAuth(page: import("@playwright/test").Page) {
  await page.addInitScript(() => {
    window.localStorage.setItem("leo.jwt", "test-jwt-token-abcdef");
    // Force full telemetry so custom domain events aren't filtered out.
    window.localStorage.setItem("leo.telemetry.mode", "full");
  });
}

test.describe("telemetry — domain events reach /api/telemetry", () => {
  test.beforeEach(async ({ page }) => {
    await mockLeoBackend(page);
    await seedAuth(page);
  });

  test("chat-reconnect (manual) emits a telemetry event", async ({ page }) => {
    const telemetry = await mockTelemetry(page);

    // Force the stream request to fail so a dropped-partial banner appears
    // (but only AFTER at least one delta arrives so `receivedAny` is true).
    let firstCall = true;
    await page.route("**/v1/chat/completions", async (route) => {
      if (firstCall) {
        firstCall = false;
        // Send one delta, then abort mid-stream.
        await route.fulfill({
          status: 200,
          headers: { "content-type": "text/event-stream", "cache-control": "no-cache" },
          body: `data: ${JSON.stringify({ choices: [{ delta: { content: "partial " } }] })}\n\n`,
        });
        return;
      }
      // Second call — the manual reconnect — succeeds.
      await route.fulfill({
        status: 200,
        headers: { "content-type": "text/event-stream", "cache-control": "no-cache" },
        body: [
          `data: ${JSON.stringify({ choices: [{ delta: { content: "done." } }] })}`,
          "data: [DONE]",
          "",
        ].join("\n\n"),
      });
    });

    await page.goto("/app/chat");
    await page.getByTestId("chat-input").fill("hi");
    await page.getByTestId("chat-send").click();

    // Manual reconnect banner surfaces once the partial stream ends.
    const manual = page.getByTestId("chat-reconnect-manual");
    await expect(manual).toBeVisible({ timeout: 10_000 });
    await manual.getByRole("button", { name: /reconnect/i }).click();

    await expect
      .poll(() => telemetry.getEventsOfKind("chat-reconnect").length, {
        timeout: 5_000,
      })
      .toBeGreaterThan(0);
    const evt = telemetry.getEventsOfKind("chat-reconnect")[0] as {
      trigger?: string;
      session_id?: string;
    };
    expect(evt.trigger).toBe("manual");
    expect(typeof evt.session_id).toBe("string");
  });

  test("merge-banner events fire when another device updates the session", async ({ page }) => {
    const telemetry = await mockTelemetry(page);

    await page.goto("/app/chat");
    await expect(page.getByRole("heading", { name: /start a conversation/i })).toBeVisible();

    // Simulate a background merge coming from the sync layer.
    await page.evaluate(() => {
      window.dispatchEvent(
        new CustomEvent("leo:chat-merged", {
          detail: {
            id: "s_remote_1",
            title: "From other device",
            addedFromRemote: 2,
            removedFromLocal: 0,
            remoteVersion: 3,
            mergedVersion: 4,
            kind: "background",
          },
        }),
      );
    });

    await expect
      .poll(() => telemetry.getEventsOfKind("chat-merge-banner").length, {
        timeout: 5_000,
      })
      .toBeGreaterThan(0);
    const evt = telemetry.getEventsOfKind("chat-merge-banner")[0] as {
      merge_kind?: string;
      added_from_remote?: number;
      merged_version?: number;
    };
    expect(evt.merge_kind).toBe("background");
    expect(evt.added_from_remote).toBe(2);
    expect(evt.merged_version).toBe(4);
  });
});
