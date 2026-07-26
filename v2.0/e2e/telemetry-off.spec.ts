import { test, expect } from "@playwright/test";
import { mockLeoBackend, mockTelemetry } from "./mocks";
import { freezeNonVisual } from "./deterministic";

async function seedAuthTelemetryOff(page: import("@playwright/test").Page) {
  await page.addInitScript(() => {
    window.localStorage.setItem("leo.jwt", "test-jwt-token-abcdef");
    // Privacy: user opted out of telemetry entirely.
    window.localStorage.setItem("leo.telemetry.mode", "off");
  });
}

test.describe("privacy — telemetry mode 'off' suppresses non-essential events", () => {
  test.beforeEach(async ({ page }) => {
    await freezeNonVisual(page);
    await mockLeoBackend(page);
    await seedAuthTelemetryOff(page);
  });

  test("no vitals/domain events reach /api/telemetry while off, but runtime errors still ship", async ({
    page,
  }) => {
    const telemetry = await mockTelemetry(page);

    await page.goto("/app/chat");
    await expect(page.getByRole("heading", { name: /start a conversation/i })).toBeVisible();

    // Send a chat message so we would normally emit reconnect / assistant-
    // metadata style domain events. With telemetry off, none of these
    // must reach the endpoint.
    await page.getByTestId("chat-input").fill("hi");
    await page.getByTestId("chat-send").click();
    await expect(page.getByTestId("chat-assistant").last()).toContainText("Hello from LEO.", {
      timeout: 10_000,
    });

    // Also dispatch a fake background merge — normally emits a merge-banner
    // telemetry event; must be dropped under mode=off.
    await page.evaluate(() => {
      window.dispatchEvent(
        new CustomEvent("leo:chat-merged", {
          detail: {
            id: "s_privacy_1",
            title: "Should not leak",
            addedFromRemote: 1,
            removedFromLocal: 0,
            remoteVersion: 2,
            mergedVersion: 3,
            kind: "background",
          },
        }),
      );
    });

    // Give telemetry ~1.5s to (not) send anything.
    await page.waitForTimeout(1_500);

    // Zero non-essential events must have hit the endpoint.
    expect(telemetry.getEventsOfKind("chat-merge-banner")).toEqual([]);
    expect(telemetry.getEventsOfKind("chat-reconnect")).toEqual([]);
    expect(telemetry.getEventsOfKind("chat-optimistic-rollback")).toEqual([]);
    expect(telemetry.getEventsOfKind("web-vital")).toEqual([]);

    // Essential error telemetry is still transmitted.
    // We invoke the app's own reporter so this is a black-box check of
    // shouldSendKind() — runtime errors + unhandled rejections are the
    // documented essentials and must bypass the opt-out.
    await page.evaluate(() => {
      window.dispatchEvent(
        new ErrorEvent("error", {
          message: "synthetic error for privacy test",
          filename: "test.js",
          lineno: 1,
          colno: 1,
          error: new Error("synthetic error for privacy test"),
        }),
      );
    });

    await expect
      .poll(() => telemetry.getEventsOfKind("runtime-error").length, {
        timeout: 5_000,
      })
      .toBeGreaterThanOrEqual(1);
  });
});
