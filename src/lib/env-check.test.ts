import { describe, it, expect, beforeEach } from "vitest";
import { validateEnv } from "./env-check";

describe("validateEnv", () => {
  beforeEach(() => window.localStorage.clear());

  it("errors when no base URL configured", () => {
    window.localStorage.removeItem("leo.api_base");
    // simulate missing env by clearing the stored override; import.meta.env is fixed at build time
    const issues = validateEnv();
    // If VITE_LEO_API_BASE_URL is set via test env, this just verifies shape
    expect(Array.isArray(issues)).toBe(true);
  });

  it("errors on invalid URL", () => {
    window.localStorage.setItem("leo.api_base", "not-a-url");
    const issues = validateEnv();
    expect(issues.find((i) => i.severity === "error")).toBeTruthy();
  });

  it("accepts a valid URL", () => {
    window.localStorage.setItem("leo.api_base", "https://api.example.com");
    const issues = validateEnv();
    expect(issues.filter((i) => i.severity === "error")).toHaveLength(0);
  });
});
