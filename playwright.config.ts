import { defineConfig, devices } from "@playwright/test";

const isSmokeTest = process.argv.some((arg) => arg.includes("smoke.spec.ts"));
const PORT = Number(process.env.PORT ?? (isSmokeTest ? 4174 : 3000));
const BASE_URL = process.env.E2E_BASE_URL || `http://127.0.0.1:${PORT}`;

export default defineConfig({
  testDir: "./e2e",
  timeout: 60_000,
  fullyParallel: true,
  retries: process.env.CI ? 2 : 0,
  reporter: process.env.CI ? [["list"], ["html", { open: "never" }]] : "list",
  use: {
    baseURL: BASE_URL,
    trace: "on-first-retry",
    screenshot: "only-on-failure",
    video: "retain-on-failure",
  },
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }],
  webServer:
    // If E2E_BASE_URL is provided (e.g. smoke job pre-boots the server), skip webServer
    process.env.E2E_BASE_URL
      ? undefined
      : {
          // Use Nitro node preset output — vite preview requires dist/server/server.js
          // which only exists for the local-dev server entry, not the Vercel preset.
          command: `node .output/server/index.mjs`,
          url: BASE_URL,
          reuseExistingServer: !process.env.CI,
          timeout: 120_000,
          stdout: "pipe",
          stderr: "pipe",
          env: {
            PORT: String(PORT),
            HOST: "127.0.0.1",
          },
        },
});
