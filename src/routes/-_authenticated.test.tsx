import { describe, it, expect, beforeEach } from "vitest";
import { Route } from "./_authenticated";
import { setToken } from "@/lib/leo-client";

describe("_authenticated route gate", () => {
  beforeEach(() => {
    setToken(null);
  });

  it("redirects to /login when no token", () => {
    setToken(null);
    const beforeLoad = Route.options.beforeLoad as (args: {
      location: { href: string };
    }) => unknown;
    expect(() => beforeLoad({ location: { href: "/app" } })).toThrow();
  });

  it("handles unauthenticated state redirect", () => {
    const beforeLoad = Route.options.beforeLoad as (args: {
      location: { href: string };
    }) => unknown;
    expect(() => beforeLoad({ location: { href: "/app" } })).toThrow();
  });
});
