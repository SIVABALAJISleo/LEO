import { describe, it, expect, vi, beforeEach } from "vitest";
import {
  leoJson,
  getApiBase,
  setApiBase,
  setToken,
  getToken,
  LeoError,
  setDebugMode,
  getDebugMode,
} from "./leo-client";

function mockFetch(opts: { body?: unknown; status?: number }) {
  const status = opts.status ?? 200;
  const body = typeof opts.body === "string" ? opts.body : JSON.stringify(opts.body ?? {});
  const spy = vi
    .fn()
    .mockResolvedValue(
      new Response(body, { status, headers: { "Content-Type": "application/json" } }),
    );
  vi.stubGlobal("fetch", spy);
  return spy;
}

describe("leo-client", () => {
  beforeEach(() => {
    setApiBase("http://localhost:8000");
    setToken(null);
    setDebugMode("off");
  });

  it("uses configured API base", () => {
    setApiBase("https://api.example.com");
    expect(getApiBase()).toBe("https://api.example.com");
  });

  it("attaches bearer token", async () => {
    setToken("tk_test");
    const fetchSpy = mockFetch({ body: { ok: true } });
    await leoJson("/api/v1/leo/metrics");
    const headers = (fetchSpy.mock.calls[0][1] as RequestInit).headers as Headers;
    expect(headers.get("Authorization")).toBe("Bearer tk_test");
  });

  it("POSTs auth login to the correct route", async () => {
    const fetchSpy = mockFetch({ body: { access_token: "abc" } });
    const res = await leoJson<{ access_token: string }>("/api/v1/auth/login", {
      method: "POST",
      body: JSON.stringify({ email: "a@b.com", password: "x" }),
    });
    expect(res.access_token).toBe("abc");
    expect(fetchSpy.mock.calls[0][0]).toBe("http://localhost:8000/api/v1/auth/login");
  });

  it("POSTs signup to the correct route", async () => {
    const fetchSpy = mockFetch({ body: { access_token: "abc" } });
    await leoJson("/api/v1/auth/signup", {
      method: "POST",
      body: JSON.stringify({ email: "a@b.com", password: "x" }),
    });
    expect(fetchSpy.mock.calls[0][0]).toBe("http://localhost:8000/api/v1/auth/signup");
  });

  it("hits chat completions endpoint", async () => {
    const fetchSpy = mockFetch({ body: { choices: [] } });
    await leoJson("/v1/chat/completions", { method: "POST", body: "{}" });
    expect(fetchSpy.mock.calls[0][0]).toBe("http://localhost:8000/v1/chat/completions");
  });

  it("hits orchestrate endpoint", async () => {
    const fetchSpy = mockFetch({ body: {} });
    await leoJson("/api/v1/leo/orchestrate", { method: "POST", body: "{}" });
    expect(fetchSpy.mock.calls[0][0]).toBe("http://localhost:8000/api/v1/leo/orchestrate");
  });

  it("throws LeoError with backend detail on non-2xx", async () => {
    mockFetch({ status: 400, body: { detail: "bad input" } });
    await expect(leoJson("/api/v1/leo/metrics")).rejects.toMatchObject({
      status: 400,
      message: "bad input",
    });
  });

  it("clears token and fires unauthorized handler on 401", async () => {
    const { setUnauthorizedHandler } = await import("./leo-client");
    setToken("tk");
    const onUnauth = vi.fn();
    setUnauthorizedHandler(onUnauth);
    mockFetch({ status: 401, body: {} });
    await expect(leoJson("/api/v1/leo/metrics")).rejects.toBeInstanceOf(LeoError);
    expect(getToken()).toBeNull();
    expect(onUnauth).toHaveBeenCalled();
  });

  it("persists debug mode", () => {
    setDebugMode("verbose");
    expect(getDebugMode()).toBe("verbose");
  });
});
